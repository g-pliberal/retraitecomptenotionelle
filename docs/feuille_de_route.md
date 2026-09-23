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
régimes est finie : <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->90<!--/--> lignes d'inventaire, plus aucune ligne « à modéliser »,
<!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=partiel)-->38<!--/--> fiches partielles dont chaque mur est documenté dans `regimes.md` et
`limites.md` §4. Continuer sur cet axe rapporte peu : les manques restants
portent sur des populations minuscules ou des barèmes que personne ne publie.
Les gains sont sur ce qui porte les résultats de tête du README : les agrégats
de la page Coût, la part patronale, les taux de cotisation qui sont la matière
même des scénarios notionnels, et l'étalon qu'est le scénario 1.

Un coût transversal pèse sur l'ordre : chaque changement du MODÈLE se paie deux
fois, dans `src/retraite_notionnelle/scenarios/actuel.py`
(<!--chiffre:lignes(src/retraite_notionnelle/scenarios/actuel.py)-->5 554<!--/--> lignes)
et dans le portage `moteur/js/` (<!--chiffre:lignes(moteur/js/*.js)-->36 278<!--/--> lignes), puis dans les
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
- *Les programmes 195, 197 et 198 ont fini par servir, le 20 septembre 2026,
  mais pas à ce que l'action leur demandait.* Apportés par l'utilisateur — le
  dépôt ne sait pas les récupérer —, ils ne portent aucun taux employeur : les
  cotisations de la RATP y sont en millions d'euros, salariés et employeur
  confondus, et les marins n'y ont que leur subvention. Ils donnent en revanche
  le taux d'ÉQUILIBRE que la convention ci-dessus laisse dehors : la
  subvention rapportée aux pensions servies, 0,60 à 0,64 à la SNCF et 0,58 à
  0,62 à la RATP, chaque année de 2012 à 2023, saisis dans
  `regimes/pap_regimes_subventionnes.csv` et écrits dans `limites.md`. Et ils
  disent que depuis 2025 cette subvention ne va plus au régime : la CNAV
  l'équilibre, l'État la compense, voir `docs/regimes.md`.

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

    **Démenti le 21 septembre 2026.** Ce décret ne touche pas la vieillesse :
    c'est le point exceptionnel du plan Barrot, sur la seule cotisation maladie
    du salarié. Les deux années sont justes, et la conclusion tirée ici était
    une déduction faite sur un titre de décret. Le détail et ses trois sources
    sont sous l'action 41 et au § 4 de `limites.md` ; la règle du garde-fou,
    elle, reste bonne — un décret de cette forme doit être vu, quitte à
    s'expliquer ensuite.
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

- **19 septembre 2026, la dette du pays sous le stock : l'échelle qui
  manquait.** Demandé par l'utilisateur : un graphique de la dette publique en
  part du PIB dans la page Coût, pour voir d'un coup d'œil si la proposition
  fait mieux ou moins bien que le système actuel. La section de la dette
  disait « celle que l'État porte déjà, que cette page ne chiffre pas » ; elle
  la chiffre. Livré : `data/reference/macro/dette_publique.csv`, la dette des
  administrations publiques au sens de Maastricht en part du PIB, 1995-2025,
  certifiée depuis la BDM de l'INSEE (idbank 010777608, quatrième trimestre
  de la seule série en base 2020 — les annuelles de la BDM sont restées en
  bases 2010 et 2014, et un rapport au PIB ne se lit que dans la base du PIB
  qu'on lui oppose) ; la série dans `ComptesRetraite` et dans le paquet ;
  `Dette.dette_publique_observee`, `annee_dette_publique` et
  `dette_publique(scenario, annee)` dans `cout.py`, portés dans `cout.js` ; un
  second graphique dans le dépliant de la dette, dans les deux rendus : la
  dette observée de 1995 à 2025, puis, à compter de 2025, cette dette tenue à
  plat en part du PIB à laquelle le système actuel et la proposition ajoutent
  leur seul stock. L'hypothèse est dite sur la page : ce n'est pas une
  prévision de la dette publique, le reste du budget n'est pas modélisé, et
  une dette qui bougerait pour d'autres raisons décalerait les deux courbes
  d'un même bloc sans changer leur écart. Les systèmes 2 et 3 ne sont pas
  tracés là — leur réserve de cinq fois le PIB dessinerait un pays qui a
  remboursé quatre fois sa dette, ce qu'aucun système notionnel ne ferait, et
  son échelle écraserait l'écart qui compte ; leur stock reste dans le
  graphique et le tableau du dessus. *Mesuré* : la dette publique faisait
  **116 % du PIB fin 2025** ; à rien d'autre qui bouge, le système actuel la
  porte à **182 %** en 2070 et la proposition à **260 %**, soit 78 points de
  PIB de plus que le système actuel — l'écart entre les deux stocks, tel
  quel. Deux tests dans `test_cout.py` ; le témoin de la page Coût bouge, les
  469 témoins de simulation ne bougent pas. Ce qui reste : l'axe du graphique
  monte à 500 pour une courbe qui plafonne à 260, parce que le pas rond de
  `_sommet` saute de 50 à 100 quand cinq divisions ne suffisent plus — c'est
  la règle de tous les graphiques du site, et elle se règle là, pas ici.

- **19 septembre 2026, la proposition a ses deux courbes sur le bilan.**
  Demandé par l'utilisateur : le graphique de tête de la page Coût donnait
  au système actuel ce qui sort et ce qui rentre, et à la proposition une
  seule courbe, ce qu'elle coûterait. On ne voyait qu'une moitié de son
  compte. Livré : une cinquième courbe, « Ce qu'elle encaisserait », en jaune
  plein sous le jaune en tirets, lue dans `ressources_de("notionnel_liberal")`
  — 18 % sur les revenus d'activité, sans la contribution d'équilibre de
  l'État ni ce que la CNAF et l'Unédic versent pour des droits qu'elle ne
  sert plus —, dans les deux rendus, et la note sous la carte dit que l'écart
  entre les deux jaunes est son solde. *Mesuré* : dès 2026, la proposition
  encaisse moins qu'elle ne verse, et l'écart se voit là où la phrase « les
  comptes ne se rééquilibrent jamais » le disait sans le montrer. Seul le
  témoin de la page Coût bouge. Dans la foulée, les deux courbes de la
  proposition partent de la bascule et non plus de la dernière année
  observée : l'année d'avant la bascule, la proposition n'est pas encore
  appliquée, son point était celui du système actuel, et la courbe faisait
  un à-pic de cinq points de PIB qui ne mesurait rien — l'utilisateur l'a vu
  tout de suite.

- **20 septembre 2026, le solde sous quatre régimes uniques, et la recette
  qui suit leur taux.** Demandé par l'utilisateur : lequel des scénarios 2 à 6
  tient, et sous quel régime unique. La page Coût ne fait suivre la recette
  au taux que pour le scénario 6 ; or le régime unique des scénarios 2 à 5
  change aussi ce qui est prélevé — l'artisan passe de 9 à 25,8 %, l'État de
  82 à 15 % du traitement. Livré : `scripts/solde_fusion.py`, qui refait le
  solde 2026-2070 sous quatre barèmes — A le régime unique du modèle
  (25,83 % déplafonné), B le salarié du privé généralisé avec ses tranches et
  son plafond de huit PASS, C le régime général seul, D la moyenne des
  régimes (11,93 %) — et fait suivre la recette des scénarios 2 à 5 au taux
  effectif lu sur la grille, sous les deux conventions du dépôt : « assiette »,
  la règle du programme (taux × assiette des revenus d'activité, sans impôts
  affectés, subventions ni contribution d'équilibre), et « rapport », tout
  reconduit sauf le taux ; sept tests dans `test_solde_fusion.py`, dont un
  qui tient les scénarios 1 et 6 et les années d'avant la bascule identiques
  à la page. *Mesuré*, solde moyen 2026-2070 en points de PIB sous
  « assiette » (sous « rapport » entre parenthèses), dette accumulée en 2070 :
  système actuel −1,13 (66 % du PIB) ; proposition à 18 % −1,52 (103 %) ;
  scénario 5 sous A −1,65 (−1,04), 113 % ; sous B −1,79 (−1,17) ; sous C
  −5,15 (−4,07), 363 % ; sous D −5,59 (−4,43), 396 % ; scénario 4 sous A
  +0,75 (+1,36), réserve de 62 % ; sous C −2,75 ; scénario 3 sous A −0,07,
  à l'équilibre en 2054, sous C −4,24. Trois lectures. *B égale A* à un ou
  deux dixièmes près : le plafond ne mord que sur le cadre et le libéral, et
  les âges du régime unique ne sont lus par aucun compte. *Un taux plus bas
  n'est pas « plus négociable », il est impayable* : sous C et D, la caisse
  sert pendant vingt-cinq ans les pensions acquises sous l'ancien droit avec
  la moitié des cotisations, et le déficit annuel dépasse cinq points de PIB
  jusqu'en 2050. *La proposition à 18 % fait la même chose, en moins fort* :
  face au scénario 4, qui est elle-même au taux du statut pivot, les 18 %
  coûtent 2,3 points de PIB par an sur toute la fenêtre, et son solde n'est
  meilleur que celui du scénario 5 que parce qu'elle recalcule le stock. Ce
  qui tient sous les règles du programme, c'est donc un compte notionnel
  au taux d'aujourd'hui, part patronale comprise : rétroactif (4) il dégage
  une réserve, prospectif (5) il coûte 1,65 point par an et ne s'équilibre
  pas avant 2070, ou 1,04 si les impôts affectés restent. Ce que le script
  ne dit pas : le taux effectif de B et C est lu sur treize carrières, non
  sur la distribution nationale des salaires ; le coefficient d'équilibre
  n'est toujours pas appliqué ; rien n'est porté dans `moteur/js/`, la page
  Coût gardant sa convention — la porter demanderait un `bareme` sur
  `RegimeFusionne`, lu par `compte.js`, et la recette des scénarios 2 à 5
  dans `cout.js`.

- **21 septembre 2026, le stock converti à 64 ans pour qui est parti à
  l'âge légal de sa génération.** Demandé par l'utilisateur, sur un point de
  droit : les scénarios rétroactifs recalculent les pensions déjà servies
  au diviseur de l'âge de départ, et un assuré parti à 60 ans en 2010 est
  parti à l'âge que sa loi lui ouvrait — lui compter après coup quatre ans
  de rente en plus est une atteinte aux effets légitimement attendus d'une
  situation acquise (décision 2013-682 DC). Le point de départ était
  faux : la session avait écrit que le modèle « savait déjà » convertir le
  stock à l'âge légal, alors que les scénarios rétroactifs ne lisent aucun
  âge de référence (§4 de `methodologie.md`) — ce n'est que le diviseur.
  Livré : `scripts/stock_age_legal.py`, qui prend le diviseur de 64 ans
  pour toute liquidation d'avant la bascule faite à l'âge légal ou après,
  sous deux lectures de l'âge légal — `droit_commun`, celui du régime
  général pour la génération, et `tout_droit`, celui que le droit de
  l'assuré lui ouvrait, régime spécial et carrière longue compris —, plus
  `acquis`, la même règle pour les droits figés des scénarios 3 et 5 ; cinq
  tests dans `test_stock_age_legal.py`. *Mesuré*, sur la proposition, en
  points de PIB et sous la convention de la page : solde moyen 2026-2070 de
  −1,52 à −1,61 sous `droit_commun` (−0,38 en 2026, nul en 2050, dette de
  2070 de 103 à 110 % du PIB) et à −1,76 sous `tout_droit` (−0,72 en 2026,
  dette 122 %) ; 270 couples touchés sur la grille dans le premier cas, 525
  dans le second. Sur les retraités d'avant la bascule, le salarié au
  salaire moyen né en 1950, parti à 60 ans, regagne 8,2 %, celui de 1960
  4,3 %, le fonctionnaire sédentaire de 1955 1,6 % ; le cadre et l'artisan
  partis à 64 ans ou après ne bougent pas. Sous `tout_droit`, l'actif de la
  fonction publique parti à 57 ans regagne 25 %, l'agent de conduite parti
  à 52 ans 50 %, le militaire parti après dix-sept ans de services 80 % :
  c'est le prix de ne faire payer l'âge à personne. Sur les scénarios 3 et
  5, convertir les droits acquis des générations 1961 à 1967 à leur âge
  légal plutôt qu'à 64 ans coûte cinq centièmes de point. Ce que le script
  ne dit pas : la variante ne touche pas ceux partis avant leur âge légal,
  qui gardent le diviseur de leur âge ; rien n'est porté dans
  `moteur/js/`.

- **21 septembre 2026, la proposition à 18 %, prospective.** Demandé par
  l'utilisateur, à la suite de la question « quelle version passe
  législativement » : le scénario 6 est rétroactif par construction, et
  c'est ce qui l'expose ; la variante qui garde tout le reste — 18 %, pilier
  capitalisé, garantie vieillesse relevée — et laisse le stock intact est
  le scénario 5 à 18 %. Livré : `scripts/proposition_prospective.py`, qui
  bâtit le sixième système sur `prospectif` au lieu de `retroactif` et le
  fait traiter par la page Coût comme une réforme prospective (courbes du
  système actuel jusqu'à la bascule, stock sur les prix, réversion servie
  avant la bascule) ; quatre tests dans `test_proposition_prospective.py`.
  *Mesuré*, en points de PIB sous la convention de la page : solde −4,73 en
  2026, −4,80 en 2040, −1,43 en 2070, moyenne 2026-2070 de **−3,92** contre
  −1,52 pour la proposition rétroactive et −1,13 pour le système actuel ;
  dette accumulée en 2070 de 278 % du PIB contre 103 % ; coefficient
  d'équilibre de 2070 à 0,84. La garantie, hors du solde, coûte 0,38 à 0,45
  point au lieu de 0,48 à 0,69 : moins de pensions tombent sous le plancher
  quand le stock n'est pas recalculé. Sur les cas types, la génération 1965
  retrouve le scénario 5 à un point près, la génération 2000 rejoint la
  proposition rétroactive à un ou deux points près, et les générations
  intermédiaires sont entre les deux : −18,6 % au salaire moyen né en 1975
  contre −40,0 % rétroactif et −12,3 % sous le scénario 5. Ce que cela
  dit : rendre la proposition prospective enlève l'obstacle juridique et
  double son coût de transition, parce que le stock est payé en entier avec
  dix points de cotisation en moins ; face au scénario 5 sous la même
  convention de recette (−1,65, note du 20 septembre), les 18 % coûtent
  toujours 2,3 points par an. Ce que le script ne dit pas : la variante
  n'est pas portée dans `moteur/js/`, et la page garde son scénario 6
  rétroactif.
  *Décision de l'utilisateur, le même jour : la variante prospective n'est
  pas retenue — à −3,92 point de PIB par an elle n'est pas finançable. La
  proposition reste rétroactive ; le script demeure, comme mesure de ce
  que la rétroactivité finance.*

- **20 septembre 2026, `main` réparé une seconde fois, et le solde du
  scénario 6 rechiffré.** Demandé par l'utilisateur : le solde du scénario 6
  « n'est toujours pas bon », mettre à jour les graphiques de la page Coût et
  le rechiffrer. Trouvé en chemin : le commit qui a porté le réglage des frais
  du pilier sur `main` (391dd61) avait été rebasé sur celui de la reprise
  calculée sur le patrimoine (602bd3e) sans que ses cinq conflits soient
  résolus — `moteur/js/pages.js` et `web/pages.py` portaient encore leurs
  marqueurs, le site ne se chargeait plus depuis ce commit, et le site publié
  en était resté au commit d'avant. C'est la seconde fois (voir edae501).
  Réparé en gardant les deux côtés — la reprise calculée sur le patrimoine
  (`reprise` vide) ET le réglage `frais` — par deux sessions à la fois, à
  l'identique : celle des frais a poussé la sienne (ebc6527) pendant que
  celle-ci faisait la même, et le rebasage n'a laissé que le rechiffrage.
  Témoins régénérés — ceux du commit fautif avaient été produits avant le
  rebasage et ne portaient pas le champ des frais. *Rechiffré*,
  Python et JavaScript à l'identique, sous la convention de la page : solde du
  scénario 6 de −0,90 en 2026, −1,12 en 2030, −1,79 en 2040, −2,03 en 2050,
  −1,52 en 2060, −0,63 en 2070, **−1,52 point de PIB en moyenne 2026-2070**,
  jamais à l'équilibre, coefficient de 2070 de 0,92, dette accumulée de 103 %
  du PIB en 2070 contre 66 % pour le système actuel (−1,13 en moyenne). Rien
  n'a bougé dans le modèle : les graphiques de la page Coût étaient déjà
  ceux-là, c'est le site qui ne les montrait plus. Le tableau du README, qui
  portait encore les −1,93 et 0,89 du 18 septembre, est remis aux valeurs du
  jour. Ce qui reste, et que l'utilisateur veut voir ensuite : ce qui peut
  réduire ce déficit.
- **21 septembre 2026, la justification sur le site : ce qui pouvait nous
  arrêter.** Demandé par l'utilisateur, après la décision de garder le
  scénario 6 : montrer sur le site que les principaux points de blocage ont
  été regardés. Livré : un dépliant de plus sur la page Programme, « Ce qui
  pouvait nous arrêter, et ce que nous en avons fait », entre les étapes de
  la transition et « Tout vérifier » — un tableau à cinq lignes, la fusion
  des régimes, les pensions déjà servies recalculées, le taux de 18 %, la
  garantie vieillesse, le chemin législatif, avec pour chacune ce qui a été
  mesuré et ce qu'on en retient —, dans les deux rendus, témoin de la page
  régénéré. Ses chiffres sont DATÉS et la section le dit : ils viennent des
  trois scripts des 20 et 21 septembre (`solde_fusion.py`,
  `stock_age_legal.py`, `proposition_prospective.py`), que le portage ne
  porte pas, et la page d'accueil ne calcule rien. À reprendre à la main si
  l'un des trois est relancé sur une autre base : rien ne les tient. Une
  phrase engage le parti au-delà de ce qui a été décidé en session et se
  relit avant publication : celle qui chiffre la parade du stock à l'âge
  légal sans dire si elle est retenue.

- **20 septembre 2026, la convention `rapport` chiffrée, et ce qu'elle
  n'est pas.** Demandé par l'utilisateur, à la suite du rechiffrage :
  combien vaut le scénario 6 sous l'ancienne convention de recette, et
  comment cela se compare au système actuel. *Mesuré*, en points de PIB :
  solde moyen 2026-2070 de **−0,55** sous `rapport` contre −1,52 sous
  `assiette`, soit **0,97 point d'écart** — environ 29 Md€ par an aux euros
  de 2025, où un point de PIB vaut 29,9 Md€ ; coefficient de 2070 de 1,04
  contre 0,92 ; dette accumulée de 36 % du PIB contre 103 %. L'écart est
  stable — 0,92 point de 2030 à 2070 — sauf en 2026 et 2027, où il vaut
  2,37 et 1,74 : c'est la marche de deux ans que `_rapports_recettes`
  décrit déjà, le rapport valant 0,77 puis 0,71 avant de se poser à 0,638.
  Les cinq autres systèmes ne bougent pas d'un millième, la convention ne
  concernant que le scénario 6. *D'où vient l'écart*, poste par poste en
  2030 : `rapport` reconduit 2,74 points de ressources non contributives
  que la convention du programme ne reconduit pas — impôts et taxes
  affectés 1,46, contribution d'équilibre de l'État 1,03, subventions
  d'équilibre 0,25 —, et sa base cotisée est plus basse de 1,79 point, la
  part contributive observée multipliée par 0,638 donnant 5,81 là où 18 %
  de l'assiette mesurée donnent 7,60. Le solde net est de +0,95.
  **Ce que cela ne dit pas, et il faut l'écrire ici** : ce n'est pas un
  levier de réduction du déficit. La dépense est la même à l'euro près
  dans les deux colonnes ; seule change la recette qu'on accepte de
  compter. Les trois postes que `rapport` reconduit ont été écartés par
  décision du Parti libéral le 19 septembre 2026, et pour un motif qui ne
  se retourne pas : un compte notionnel ne crédite que ce qui est assis
  sur un revenu d'activité. `rapport` répond donc à « que percevrait la
  proposition si elle gardait les recettes du système actuel », pas à
  « que coûte-t-elle ». *Ce qu'elle déplace quand même, et qui compte pour
  l'arbitrage* : sous `assiette` le scénario 6 est 0,39 point SOUS le
  système actuel (−1,13), sous `rapport` il est 0,58 point AU-DESSUS. Le
  choix de convention retourne le sens de la comparaison avec le droit en
  vigueur — c'est la raison pour laquelle la page n'en expose aucune et
  s'en tient à celle du programme. Les deux conventions existent des deux
  côtés du portage, `cout.py` et `cout.js` ; aucune n'est un réglage du
  site.

- **20 septembre 2026, les deux postes écartés chiffrés séparément : le
  déficit tient-il dedans ?** Demandé par l'utilisateur, à la suite de la
  convention `rapport`, qui les reconduisait en bloc : chiffrer les impôts
  affectés et la contribution d'équilibre de l'État chacun de son côté, et
  dire s'il en faut plus ou moins que ce que le système actuel y met.
  Livré : `scripts/postes_ecartes.py`, qui reconduit un par un les trois
  postes que la convention du programme écarte, sans toucher à la dépense
  ni à aucun moteur ; huit tests dans `test_postes_ecartes.py`, dont celui
  qui tient la référence du script égale au solde de la page à 1e-15 —
  sans lui, une dérive d'un millième passerait dans chaque chiffrage sans
  rien dire.

  *Mesuré*, solde moyen 2026-2070 en points de PIB, la proposition étant à
  −1,52 et le système actuel à −1,13 ; un point de PIB vaut 29,9 Md€ aux
  euros de 2025 :

  | chiffrage | moyenne | pire année | équilibre |
  |---|---|---|---|
  | Proposition, convention du programme | −1,52 | −2,03 en 2049 | jamais |
  | + impôts et taxes affectés | −0,13 | −0,65 en 2049 | dès 2026 |
  | + contribution d'équilibre de l'État | +0,03 | −0,50 en 2049 | dès 2026 |
  | + subventions d'équilibre | −1,28 | −1,79 en 2049 | jamais |
  | + les trois | +1,67 | +1,13 en 2049 | dès 2026 |

  **La réponse à la question posée, et elle dépend d'une ligne.** Le poste
  des impôts affectés vaut 2,14 points de PIB en 2026 et 1,98 en 2070 tel
  que le COR le publie — mais un tiers en est la CSG du fonds de solidarité
  vieillesse, 0,67 point, qui rentre avec le poste et ressort aussitôt par
  le retrait, puisqu'elle paie des droits que la proposition ne sert plus.
  Net, le poste ne vaut donc que 1,47 point, et les deux lectures ne
  concluent pas pareil : **contre le poste publié, la proposition demande
  75 % de ce que le système actuel y met — moins ; contre le poste net, elle
  en demande 109 % — plus.** La contribution d'équilibre, elle, n'a pas ce
  double compte : 1,63 point en 2026, 1,51 en 2070, et la proposition en
  demande **98 %**, c'est-à-dire tout juste moins que ce que l'État y met
  déjà. Les subventions d'équilibre ne pèsent rien à cette échelle : il en
  faudrait 629 %.

  *Ce qui tranche entre les deux lectures des impôts* : la garantie
  vieillesse coûte 0,69 point en 2026 et 0,48 en 2070, contre 0,67 et 0,62
  pour la CSG du fonds. Les deux sont du même ordre, et ce n'est pas un
  hasard — la garantie REMPLACE les droits que le fonds finance. Cette CSG
  est donc déjà promise, et la lecture nette est celle qui vaut : il faut à
  la proposition un peu PLUS que les impôts affectés disponibles, un peu
  MOINS que la contribution d'équilibre.

  *Ce que le chiffrage de la contribution suppose, et qu'il faut dire* :
  elle se SUPERPOSE aux 18 %, elle ne les remplace pas. L'assiette des 18 %
  porte déjà les traitements de la fonction publique, si bien que ce
  chiffrage fait payer à l'État 18 % comme tout employeur PLUS le
  complément qu'il verse aujourd'hui. C'est bien la question posée — que
  se passe-t-il si ce poste reste intact — et ce n'est pas une lecture du
  taux d'employeur de l'État sous la proposition.

  **Aucun des deux postes ne suffit chaque année.** Sur la moyenne ils y
  sont presque ; sur le creux de 2049, où les pensions du baby-boom pèsent
  le plus, il faudrait 147 % des impôts nets et 132 % de la contribution.
  Un poste reconduit ramène donc la proposition à l'équilibre moyen, pas à
  l'équilibre annuel : le creux des années 2040-2050 reste à financer
  autrement — par la dette, qu'il reste alors 0,50 à 0,65 point de PIB à
  creuser pendant une quinzaine d'années, ou par le coefficient
  d'équilibre, que le modèle calcule et n'applique jamais.

  Ce que le script ne dit pas : il ne pose aucune doctrine, et reconduire
  un poste ne rend pas la proposition moins chère — la dépense est la même
  à l'euro près dans toutes les colonnes, un test le tient. Rien n'est
  porté dans `moteur/js/`, la page gardant la convention du programme.

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

### 11. Appliquer le coefficient d'équilibre — `archivée`

**Archivée le 20 septembre 2026, à la demande de l'utilisateur.** Elle
demandait que le coefficient d'équilibre, calculé année par année depuis
l'action 6, soit APPLIQUÉ : que les courbes de la page Coût soient celles d'un
système qui se pilote. Ce qui la rendait secondaire était nommé dans l'action
elle-même — un facteur commun ne déplace AUCUN écart entre carrières, donc
appliquer le coefficient n'aurait rien changé à ce que le site mesure page par
page. Entre-temps, l'action 62 a fait le pas qui comptait : le coefficient est
LU partout où un lecteur lit un montant. Le reste — le pilotage de l'agrégat —
est descendu dans « Ce qui est délibérément en bas », avec ce qu'il aurait
demandé, pour qui voudrait l'y reprendre.

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

### 14. La mortalité différentielle par revenu, que le diviseur ignore — `fait`

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
depuis 1941. Une mesure par POPULATION existe aussi, lue le 20 septembre 2026
dans le projet annuel de performances du programme 741 (PLF 2026) : le Service
des retraites de l'État publie l'espérance de vie à 65 ans de ses pensionnés
civils — 24,68 ans pour les femmes, 21,16 pour les hommes en 2024 — et la dit
« structurellement supérieure à celle de la population générale ». Saisie dans
`regimes/pap_regimes_subventionnes.csv` ; c'est le premier écart entre une
population de cotisants et la table commune que le dépôt tienne d'un
producteur.

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

**Ce que ça a déplacé, 20 septembre 2026 — d'abord l'axe des POPULATIONS,
avec la seule mesure qu'un producteur publie.** Le Service des retraites de
l'État donne l'espérance de vie à 65 ans de ses pensionnés civils (PAP 741 du
PLF 2026, apporté par l'utilisateur) : 24,68 ans pour les femmes, 21,16 pour
les hommes en 2024, un an de plus que l'INSEE à la population générale.

- *La mécanique, exactement celle que la marche prescrivait.* Un facteur sur
  la force de mortalité de la table générale — la survie de chaque cellule
  (âge, année) élevée à cette puissance —, calé par bissection sur la table
  du moment de l'année observée pour reproduire l'espérance publiée, tenu
  constant sur toutes les autres années en le disant. Il vaut 0,858 pour les
  hommes et 0,852 pour les femmes des fonctionnaires civils. Python
  (`facteur_population`) et JavaScript (`facteurPopulation`) concordent au
  bit près, le paquet transportant les facteurs pour que le navigateur ne
  recalibre pas. La donnée est dans
  `mortalite/esperances_vie_populations.csv`, la variante dans
  `Parametres.population_conversion`, lue par le convertisseur et le pilier
  capitalisé, sur le site sous « Population de la table », dans les témoins.
- *Le résultat, sur le fonctionnaire sédentaire, par
  `scripts/mortalite_population.py`.* Né en 1975, parti à 65 ans en 2040 : la
  table de sa population lui donne 26,39 ans de rente contre 24,88, soit
  **1,5 an**, et une pension notionnelle inférieure de **5,7 %** à capital
  égal — 44 243 € contre 46 925 € au scénario 4. Le transfert sur la vie vaut
  71 000 € au scénario 4 et **54 000 € sous le système actuel**, dont la
  pension ne bouge pas d'un euro : aucun diviseur ne l'a calculée. Sur les
  générations 1960 à 2000, l'écart va de 1,6 à 1,3 an et de 6,1 à 5,0 %,
  parce que la table générale rattrape peu à peu.

**Puis l'axe du REVENU, par les tables de l'INSEE — et c'est la question
posée qui reçoit sa réponse.**

- *La donnée, lue chez le producteur et non saisie.*
  `scripts/fetch/insee_mortalite_niveau_de_vie.py` télécharge le classeur des
  *Insee Résultats* de mai 2025 (`morta_niv.xlsx`, insee.fr répond à la
  session) et en reprend telles quelles e0, e60 et e65 de l'ensemble et des
  vingt vingtiles, par sexe, pour 2012-2016 et 2020-2024, avec le niveau de
  vie mensuel moyen de chaque vingtile. À 65 ans en 2020-2024 : 15,1 ans pour
  les 5 % d'hommes les plus modestes, 22,1 pour les 5 % les plus aisés ; 20,2
  et 25,2 chez les femmes. Le récupérateur contrôle l'ensemble de l'étude
  contre la moyenne des cinq espérances annuelles certifiées, et trouve un à
  trois dixièmes de moins, toujours du même signe — le champ et la méthode de
  l'échantillon démographique permanent. **D'où une règle de calibration** :
  un vingtile n'est pas calé sur sa valeur brute mais sur son rapport à cet
  ensemble, appliqué à la table générale ; les facteurs vont de 1,75 (hommes
  du premier vingtile) à 0,69 (dernier), et l'écart de sept ans se retrouve
  dans le modèle à un dixième près. Portage JavaScript au bit près, cette
  règle comprise.
- *Le rattachement, une convention et non une mesure.* Un cas type est placé
  au vingtile dont le niveau de vie moyen est le plus proche de son salaire
  rapporté au salaire moyen, appliqué au niveau de vie moyen des vingt
  vingtiles (`population_niveau_de_vie`) : le SMIC au quatrième, le salaire
  moyen au treizième, le cadre au dix-neuvième, le libéral au vingtième. Le
  niveau de vie est celui d'un ménage par unité de consommation, un salaire
  n'en dit qu'une partie, et c'est écrit dans `methodologie.md` §5.
- *Le résultat, treize cas types, génération 1975, par
  `scripts/mortalite_population.py --niveau-de-vie`.* Le salarié au SMIC a
  **3,0 ans de rente de moins** que la table commune ne lui en compte,
  l'exploitant agricole 3,7 de moins ; le cadre **2,7 de plus**, le libéral
  3,2 de plus, les fonctionnaires et agents des régimes spéciaux 1,4 à 2,0 de
  plus. À capital égal, une table qui le saurait servirait 12,5 % de plus au
  SMIC et 11,7 % de moins au libéral. Sur la vie, sous le système actuel :
  49 000 € retirés au SMIC, 44 000 € à l'exploitant, 173 000 € ajoutés au
  libéral, 154 000 € au cadre. Le diviseur commun transfère des modestes vers
  les aisés, dans le sens qu'on craignait, et il le fait dans les six
  scénarios : le système actuel, sans diviseur, autant que les autres.
  L'objection est donc coupée comme l'action le demandait — non parce que
  l'écart serait petit, il ne l'est pas, mais parce qu'il n'appartient pas au
  notionnel.
- *Sur le site.* Quatre populations sous « Population de la table » — les
  fonctionnaires civils, les 5 % les plus modestes, le niveau de vie médian,
  les 5 % les plus aisés —, trois témoins, et `limites.md` §5 qui porte le
  point de périmètre.

- *Ce que le diviseur commun coûte au régime, par
  `scripts/mortalite_population.py --deficit`.* Sur les têtes, les poids et
  les pensions de la trajectoire de la page Coût, la survie de chaque cas type
  corrigée de celle de son vingtile : un diviseur par vingtile baisserait la
  dépense des scénarios notionnels de **3,6 à 4,3 %** selon le scénario et
  l'année, soit quatre à cinq dixièmes de point de PIB — 12 à 15 milliards au
  PIB de 2025. Le solde moyen 2026-2070 du scénario 6 passerait de −2,21 % à
  −1,80 % du PIB, celui du scénario 4 de +1,47 % à +1,92 %. Sans corriger la
  survie, comme la page compte aujourd'hui, le chiffre serait de 3,2 à 4,1 % :
  la page sous-compte les rentes des vingtiles qui vivent longtemps. Le
  scénario 1 n'a pas de diviseur, rien n'y bouge. Sur le FLUX seul
  (`--depuis 2026`, le stock gardant le diviseur commun, comme une réforme
  s'appliquerait), l'économie monte de 1 % de la dépense en 2030 à 3,4 % en
  2050 et rejoint le régime permanent vers 2070 ; en moyenne 2026-2070, trois
  dixièmes de point de PIB au lieu de quatre à cinq. C'est un ordre de grandeur
  dont le signe est sûr et le niveau non : la grille pèse le cadre et le
  libéral à la part de leur caisse, plus que leur part réelle, et le
  rattachement par le salaire est une convention.

**Puis, le 21 septembre 2026, la mesure devient le défaut — à la demande :
« applique avec le stock compris sur tous les chiffres du site, fais en sorte
que ce soit facile de désactiver ».**

- *Un interrupteur, et un seul.* `Parametres.population_conversion` vaut
  désormais `POPULATION_PAR_NIVEAU_DE_VIE` : le convertisseur rattache chaque
  carrière — cas type, saisie du site ou relevé — au vingtile où son salaire
  la place, par `niveau_relatif`, la somme des revenus cotisés rapportée à la
  somme des salaires moyens des mêmes années, et lui sert le diviseur de ce
  vingtile, pilier capitalisé compris. `None` rend la table commune partout ;
  sur le site, « Population générale, la même pour tous ». Rien d'autre à
  toucher, et les scripts de mesure posent `None` pour chiffrer ce que le
  défaut déplace.
- *Le stock est compris*, comme demandé : les scénarios rétroactifs
  recalculent tout le monde ainsi, et les prospectifs convertissent les
  droits acquis à la bascule avec le même diviseur. La page Coût suit, par
  les pensions de ses cas types ; elle compte encore tout le monde à la
  mortalité générale, ce qui déplace son rapport de masses de moins de 1 %.
- *Ce qui a bougé.* Sans diviseur : rien, le scénario 1 est intact. Sous les
  notionnels, le SMIC gagne 12 % de pension, le cadre en perd 10 %, la
  proposition gagne quatre dixièmes de point de PIB de solde moyen. Les
  témoins ont été régénérés, Python et JavaScript concordent au bit près.

- *Le rattachement par la pension, en option, le même jour — à la demande :
  « chiffre avec la pension plutôt que le salaire ».* Première tentative,
  écartée avant d'être livrée : comparer la pension nette aux niveaux de vie
  de la population entière classait presque tout le monde en bas — une
  pension est plus petite qu'un salaire, et les vingtiles mêlent actifs et
  retraités —, et la proposition perdait huit dixièmes de point. Retenu : le
  RANG de la pension brute parmi les retraités, lu dans la distribution DREES
  que le dépôt avait déjà (`DistributionPensions.part_sous`), le vingtile
  étant celui du rang. Circulaire sous un compte notionnel, résolu par point
  fixe en six tours au plus (`Convertisseur.resoudre`), porté en JavaScript,
  sur le site sous « Rattachement au niveau de vie », deux témoins. Le SMIC
  monte au sixième vingtile, le salaire moyen au onzième, le cadre reste au
  dix-neuvième, les départs précoces descendent. Sur les soldes moyens
  2026-2070 : la proposition à −1,78 % par la pension contre −1,52 % par le
  salaire et −1,93 % sous la table commune ; le scénario 4 à +2,02 % contre
  +2,20 % et +1,74 %. Le défaut reste le salaire : le rang parmi les
  retraités suppose que le niveau de vie suit la pension, ce qui néglige le
  conjoint et le patrimoine, et rien ne dit qu'il vaut mieux.
- *Décision du 21 septembre 2026 : le défaut reste le salaire.* Le patrimoine
  a été demandé et ne se chiffre pas : aucun producteur ne publie de table de
  mortalité par patrimoine en France — le niveau de vie de l'INSEE en porte
  les revenus, pas le stock —, et le modèle ne connaît le patrimoine de
  personne. Si une telle table paraît, elle entre comme une population de
  plus, un facteur par sexe et un rattachement à écrire.

**Ce qui reste.** Le rattachement est le maillon faible : un salaire n'est pas
un niveau de vie, et une carrière n'est pas un ménage. Une lecture de la
distribution des niveaux de vie des RETRAITÉS par vingtile — l'INSEE la
publie dans l'enquête Revenus fiscaux et sociaux — permettrait de rattacher
par la pension plutôt que par le salaire. Le facteur reste constant dans le
temps ; l'*Insee Première* note que l'écart s'est ACCRU entre les deux
périodes, ce que les deux jeux du fichier permettent de mesurer et que le
modèle ne fait pas encore. Et la grille de cas types n'est pas une population :
le transfert agrégé, en milliards, demanderait la distribution des pensions
par niveau de vie, que le dépôt n'a pas.

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
  *Repris le 20 septembre 2026.* Dix réserves étaient devenues quatorze en
  trois jours : chaque chantier de la page y ajoutait la sienne, et le titre
  chiffré tenait le compte. Trois étaient des réglages (le stock à la bascule,
  la reprise sur succession, le coefficient d'équilibre), deux décrivaient un
  système (ce que la recette suit, la réversion), cinq disaient sous cinq
  angles que le modèle compte des générations. Les réglages sont dits sous
  leur réglage ou dans leur dépliant, les deux descriptions sont deux notes de
  « Recettes et dépenses, poste par poste », les cinq sont devenues deux. Il en
  reste cinq, sous un titre sans nombre, et le test plafonne la liste à huit :
  la prochaine réserve en fusionne une.

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

**Reprise du 21 septembre 2026 : six exemples de plus, et une leçon de plus.**
Le compte passe de vingt-deux à vingt-huit, et deux règles qui n'avaient aucun
témoin en ont maintenant : les trimestres accordés au titre des enfants et la
majoration de 10 %. Elles n'en avaient pas pour une raison de FORME, et c'est
ce qui a demandé le vrai travail : aucune caisse ne publie une carrière entière
dont elle donne la durée d'assurance — ce qu'elle publie, c'est le nombre de
trimestres ajoutés PAR ENFANT et le TAUX de la majoration. Deux grandeurs
neuves les mesurent sans rien recalculer du modèle dans le test, ce qui aurait
été circulaire : `trimestres_de_majoration_enfants` rejoue la MÊME carrière
sans enfant et compare les deux durées — l'écart ne dépend ni de l'âge
d'entrée ni de la durée requise de la génération —, et
`majoration_enfants_sur_pensions` rapporte la majoration servie à la somme des
pensions de régime. Les six tombent justes : 16 trimestres pour deux enfants au
régime général (4 de maternité + 4 d'éducation, fiche Cnav 6.2b), 24 pour
trois, 8 pour deux enfants nés avant 2004 dans la fonction publique, 4 pour
deux nés depuis ; et 10 % exactement sur une carrière surcotée à 58,125 %, au
taux plein, et minorée à 41,25 %.

Ce dernier trio est ce que la circulaire 2022-26 tient à dire et que le modèle
aurait pu manquer : « la surcote majore la retraite et fait partie intégrante
de l'avantage de base », donc la majoration « est calculée sur la base du
montant annuel de la retraite, majorée par la surcote » — 10 % × (600 + 22,50)
= 62,25. C'est un ORDRE D'OPÉRATIONS et non un barème : appliquer les 10 % à
la pension d'avant la surcote rendrait 9,52 % de celle d'après. Les deux
grandeurs ont été mises à l'épreuve avant d'être crues — un chiffre faussé dans
le témoin fait bien tomber le test, sans quoi elles n'auraient rien prouvé.

**La leçon de plus : une circulaire annulée ne certifie plus rien.** Les six
témoins de carrière longue citaient la circulaire Cnav 2026-17 du 12 juin 2026,
que la 2026-29 du 4 septembre annule et remplace. Ses âges et ses durées ont
été relus ligne à ligne dans la circulaire en vigueur — aucun n'a bougé — mais
les témoins citent désormais celle qui fait foi. C'est la leçon de juillet d'un
cran plus loin : une table certifiée l'est à une date, et une SOURCE aussi.

**Et une alerte levée sans rien changer.** La fiche service-public F16336 écrit
que « l'âge minimum […] est abaissé d'un an si vous êtes né à partir du 1er
avril 1965 et si vous bénéficiez d'au moins 1 trimestre de majoration
d'assurance maternité, adoption ou d'éducation » — une règle qui, prise au mot,
déplacerait d'un an le départ de presque toutes les mères nées depuis 1965.
L'article L. 161-17-2 a donc été lu dans sa version en vigueur
(LEGIARTI000053280889) : il ne porte aucun abaissement de ce genre, et son
échelle par génération est exactement celle du dépôt, que la circulaire 2026-07
reprend à l'identique. La phrase vulgarise l'effet des trimestres d'enfants sur
la carrière longue, que le dépôt porte déjà. **Le texte l'emporte sur la
fiche** — et c'est le troisième cas où la vérification d'un écart apparent ne
coûte que la lecture du texte, mais où ne pas la faire aurait coûté un an.

**Ce qui reste sans exemple publié**, et qui est donc encore transcrit du seul
texte : les vingt-quatre et vingt-trois meilleures années des parents (la
circulaire d'application n'est pas parue), la durée requise propre aux
catégories actives, la liquidation unique des régimes alignés, le minimum
garanti de la fonction publique, la surcote parentale. Et les trois exemples de
réputés cotisés de la circulaire 2026-29, qui sont publiés mais ne se rejouent
pas : ils arbitrent entre des périodes assimilées de nature différente, que le
modèle ne distingue pas dans une carrière qu'il synthétise — l'exemple servira
de témoin APRÈS ce portage, pas pour le guider.

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

### 34. Un test qui confronte les affirmations du site au modèle — `fait`

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

**Fait le 20 septembre 2026.** 244 entrées au catalogue — 192 vérifiées,
6 contredites, 33 hors modèle, 13 sans portée — et 122 contrôles, soit 478
tests de plus : un par entrée pour la présence de l'extrait, un par entrée qui
engage quelque chose pour le contrôle, un par affirmation hors modèle pour sa
source, plus les trois qui tiennent la forme, l'exhaustivité et l'absence de
contrôle orphelin. La suite prend cinquante secondes de plus : le seul
contrôle cher est celui de l'autre convention de recette, qui recalcule le
coût agrégé.

**Un quatrième état, `hors_modele`, et la page Risque l'a imposé.** Elle est
une revue de littérature : ce que la Russie a cessé de payer en 1996, ce que
la Grèce a coupé, ce que les juges en ont fait. Aucun contrôle du modèle ne
tranche cela, et le déclarer `sans_portee` serait mentir — une affirmation sur
le monde peut être fausse. Le test exige alors ce que le dépôt exige partout
ailleurs : la source, citée dans la page même, et un test par entrée la
cherche dans le texte rendu.

*Les quatre phrases que le catalogue a fait tomber, et ce qu'elles sont
devenues.*

- **La jumelle, dans le dépliant de transition.** « La bascule ne reprend
  aucun droit acquis et ne touche à aucune pension déjà versée », quatre
  lignes au-dessus du tableau qui dit le contraire. Remplacée par ce que le
  modèle fait : « La bascule recalcule tout, depuis la première cotisation »,
  et l'étape 2 dit « y compris celles dont la pension est déjà liquidée ».
  L'étape 6 suivait le même chemin — « la dernière pension calculée en partie
  sous l'ancien barème » laissait croire à un barème conservé ; elle parle
  maintenant de cotisations versées aux anciens taux, ce qui est ce que le
  compte porte. Le contrôle `proposition_retroactive` le tient : la pension
  d'une carrière liquidée en 2012 s'écarte de celle du droit en vigueur, et
  aucun rapport du coût ne vaut un sur les années observées.
- **« Ce facteur est supérieur à un chaque année »**, en tête des Cas types.
  Faux depuis le 19 septembre, jour où la recette de la proposition est
  devenue ses 18 % appliqués à l'assiette mesurée : le coefficient est passé
  sous un sur toutes les années projetées, et vaut 0,92 en 2070. La clé de
  lecture ne promet plus de signe, elle dit que le niveau des cases dépend du
  facteur, dans les deux sens.
- **« Lire les 0,92 comme une économie de −9 % »**, sur la page Coût. Le même
  retournement, et il se lisait à l'écran : la note parlait d'une marge
  au-dessus d'un coefficient inférieur à un, et écrivait un pourcentage
  négatif. La note a maintenant deux branches, et `note_du_coefficient_suit_son_signe`
  vérifie que celle qui s'affiche est celle du signe calculé — les deux sont
  rendues par les témoins, la première sous les réglages par défaut, la
  seconde sous ceux de `cout_regles`.
- **« L'autre lecture, plus sévère d'un point de PIB. »** Elle est plus
  GÉNÉREUSE d'un point : la convention « rapport » laisse au système 4 les
  impôts affectés et les subventions d'équilibre que la lecture retenue ne
  reconduit pas, et son solde moyen projeté vaut −0,55 % du PIB contre
  −1,52 %. La page a retenu la plus sévère, et le dit.

*Et un chiffre écrit en dur qui avait pourri* : « soit treize fois ce que les
mêmes dispositifs ajoutent au montant des pensions », sur la page Avantages.
Il vaut vingt-sept. Il est compté, désormais, sur les lignes d'âge que le
modèle chiffre.

*Deux entrées `contredite` sur des actions ouvertes.* L'action 11 porte les
quatre phrases qui promettent un pilotage annuel — « L'écart se solde chaque
année », l'étape 5 du programme, « Dépenser moins n'est pas économiser », « Un
système notionnel n'accumule ni cette dette ni cette réserve » : le modèle
calcule le coefficient et ne l'applique jamais. L'action 61, ouverte par ce
catalogue, porte « au premier euro, sans plafond » face au plafond d'assiette
de huit PASS. Le jour où l'une ou l'autre est faite, son contrôle tombe et la
phrase revient sur l'établi : c'est ce que `test_le_catalogue_est_bien_forme`
exige en refusant qu'une entrée `contredite` cite une action `fait`.

**Ce qu'il a coûté au rebasage, et c'est la meilleure preuve qu'il sert.**
Huit sessions avaient poussé entre-temps, en deux vagues. La première : la
page Risque, la refonte des réserves de la page Coût, les cinq points rendus
sortis de la fiche de paie, la part de reprise lue sur le patrimoine. Vingt et
un tests du catalogue sont tombés d'un coup — douze extraits qui n'étaient
plus dans la page, huit contrôles que le modèle avait déplacés, et la clause
d'exhaustivité sur vingt-deux phrases neuves. La seconde, huit de plus : la
garantie devenue le seul plancher, l'échelle de maturités tombée, et surtout
la lecture du coefficient d'équilibre calculée depuis le solde par
`_reglage_proposition` — une autre session avait vu la même contradiction le
même jour et l'a réparée mieux, en composant la phrase au lieu de la brancher.
Son code a été gardé, et le contrôle du catalogue vérifie désormais que les
deux pages écrivent les nombres du solde.

Aucun de ces vingt-neuf échecs n'était un faux positif : chacun nommait une
phrase ou une propriété qui avait bougé sans que personne ait à s'en souvenir.
C'est exactement ce que l'action demandait, et le coût de le tenir est
celui-là.

**Ce que le catalogue ne fait pas.** Il ne voit que les `<strong>` : une
affirmation écrite sans emphase lui échappe, et c'est le prochain cran. Il ne
juge pas non plus la prose du dépôt — `docs/`, `README.md` —, que l'action 41
tient par ses ancres. Les deux se complètent, comme elles le disaient déjà :
l'une tient les chiffres, l'autre les affirmations.

**Fin.** Le catalogue couvre les phrases fortes des six pages, la jumelle du
dépliant de transition est corrigée, et les deux contradictions connues
(étape 2 de la transition, écart soldé contre coefficient jamais appliqué) sont
dans le fichier avec l'action qui les referme — 24 pour l'une, 11 pour l'autre.

**Un troisième cas, refermé le 20 septembre 2026 sans le catalogue.** Cas
types affirmait, en texte fixe, que le coefficient d'équilibre de la
proposition « est supérieur à un chaque année ». La phrase a été écrite le 19
au soir, quand c'était vrai ; le 20 au matin, quatre changements du modèle de
coût (impôts affectés, garantie, recours, succession) l'avaient fait passer
sous un sur les quarante-cinq années projetées, et la page Coût du même site
chiffrait 0,92 en 2070 pendant que Cas types promettait une marge. Le parcours
de présentation demandait de lire la phrase à voix haute en réponse à « tout
est rouge, donc les pensions baissent ? ». C'est le mode de panne 2, une
page qu'une autre dément, et il n'a tenu que douze heures. La phrase est
désormais CALCULÉE depuis le solde, dans les deux moteurs
(`_reglage_proposition`, `_lecture_reglage_proposition`), la note de Coût
lit le coefficient dans les deux sens au lieu de supposer une marge, et
`test_cas_types_dit_du_reglage_ce_que_le_solde_dit` exige que les deux pages
disent ce que le solde dit. Le tableau des soldes du README, faux lui aussi
(−1,93 % et 0,89 pour −1,52 % et 0,92), est tenu par
`test_le_README_donne_le_solde_que_la_page_cout_calcule`. Le parcours de
présentation dit maintenant de ne pas promettre de marge. Ce que l'action
garde à faire : le catalogue, pour que la prochaine phrase fixe ne puisse pas
entrer sans qu'on ait dit ce qu'elle engage.

---

### 35. Les recettes et les dépenses du scénario 6, chiffrées toutes les deux — `fait`

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

   **Ce que la sortie coûte, remesuré le 20 septembre 2026** : **1,395 point de
   solde moyen**. Sur 2026-2070, le scénario 6 passe de −0,76 % du PIB, poste
   reconduit, à **−2,16 %**, contre −1,13 % pour le système actuel ; il est
   plus déficitaire que lui dans 38 des 45 années, ne revient à l'équilibre sur
   aucune, et son coefficient de 2040 descend de 0,90 à 0,76.

   *Les NIVEAUX ont bougé deux fois depuis la décision, le COÛT jamais* :
   −1,12 % et −2,51 % le 19 au soir, −0,28 % et −1,67 % une fois la réversion
   sortie des cinq scénarios notionnels, −0,76 % et −2,16 % depuis que le
   profil de carrière est lu chez l'INSEE (62c5b0d). Le coût est resté
   1,395 point aux trois mesures, à un millième près : c'est une PART des
   ressources, elle ne dépend pas de ce que les pensions coûtent.
   `docs/limites.md` § 5 bis porte la même table, et dit pourquoi elle existe.

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

   **Fait le 20 septembre 2026, et pas par la fiche 4.1.** Le paragraphe
   ci-dessus recommandait de partir de la CCSS et de compléter ; la troisième
   passe avait entre-temps trouvé mieux, et c'est le classeur par régime du
   COR qui est entré : `data/reference/regimes/cotisants.csv`, 1 148 valeurs,
   21 caisses, 2010-2070, certifiée au niveau `haute` par
   `verifier_donnees.py` contre le classeur, comme `structure_financement.csv`
   qui vient du même fichier. Une seule source pour les treize caisses des
   cas types, l'Ircantec et le RCI compris, et la seule qui PROJETTE : la SNCF
   n'a plus aucun cotisant en 2070, la CNIEG cinquante et un. Le CRPCEN, publié
   en milliers sous un en-tête qui le dit, est rendu en personnes. La fonction
   publique d'État, d'un seul tenant chez le COR, est partagée entre civils et
   militaires à la clé du jaune « Pensions » — 1,63 million et 0,32 million au
   1er janvier 2024 —, tenue constante et marquée `estimee`
   (`donnees/cotisants.py`).

   Ce qui a changé dans le modèle : `_ponderation` a un CÔTÉ. Les masses de
   pensions pèsent les retraités de la caisse (DREES), les masses de
   cotisations pèsent ses cotisants (COR) ; `ponderation="egale"` confond les
   deux comme avant. Porté dans `moteur/js/cout.js`, exposé par
   `Cout.poids_cotisants`, et le dépliant « Ce que chaque carrière type pèse »
   de la page Coût porte désormais les deux colonnes.

   *Ce que ça déplace, mesuré.* Les poids de 2024 bougent le plus là où la
   caisse s'éteint ou vieillit : l'exploitant agricole passe de 4,4 % parmi les
   retraités à 1,3 % parmi les cotisants, l'agent de conduite de 0,7 % à
   0,3 %, l'agent des IEG de 0,6 % à 0,4 % ; le libéral monte de 2,0 % à
   2,8 %. Le rapport de recettes du scénario 6 passe de 0,61 à 0,64 après la
   bascule, soit un taux moyen implicite de **28,0 %** au lieu de 29,5 %,
   contre 27,9 % chez le COR pour un salarié non cadre du privé : la réserve
   que `limites.md` §5 portait — « surreprésente les régimes qui s'éteignent,
   et pousse le rapport vers le bas » — était juste, et elle vaut 1,3 point de
   taux. Sous la variante `rapport`, le scénario 6 regagne **0,28 point** de
   solde moyen 2026-2070 ; sous la convention `assiette`, celle de la page, il
   ne bouge pas d'un millième, comme la mesure du 19 septembre l'annonçait.
   Aucune pension, aucun rapport de masses, aucun témoin de simulation ne
   bouge.

   *Ce que la série ne fait pas.* Elle est du millésime de juin 2024, comme
   tout ce qui sort de ce classeur, quand le reste de la page tourne sur le COR
   2026 ; et un cotisant de caisse n'est pas une personne, un polyaffilié
   comptant dans chacune des siennes — les poids sont relatifs, comme ceux des
   retraités.
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
   et la page doit porter les deux nombres sans les confondre. **Fait le 19
   septembre 2026**, et la ligne ne le disait pas : la recette du scénario 6
   n'a jamais compté que les 18 % (`taux_cotisation_liberal`, seul lu par
   `_solde`), et le dépliant « Ce que le pilier capitalisé prélève, et pourquoi
   il n'est pas dans ce bilan » de la page Coût porte le tableau à quatre
   lignes — 18 de répartition, 5 capitalisés d'office, 5 replacés
   volontairement, 28 en tout — face aux 28 % d'aujourd'hui.

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

  [Deux corrections, et l'entrée reste telle quelle pour le reste, parce
  qu'elle date un déplacement. La RAISON écrite ici est fausse : ce poste ne
  compense pas les allègements, la TVA qui le fait finance la branche maladie,
  et le compte de la Cnav n'en porte aucune ligne. La décision tient par
  l'argument des 18 % — un impôt affecté n'ouvre de droit à personne — et le
  point 4 du volet A le dit. Les NIVEAUX, eux, ont bougé deux fois depuis :
  au 20 septembre 2026, c'est −0,76 % et −2,16 %, coefficient 2040 de 0,90 à
  0,76. Le coût de la sortie n'a pas bougé d'un millième.]
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
- *Ce qui restait du volet A est fait le 20 septembre 2026* : la série
  d'effectifs de COTISANTS (point 3) est entrée, et elle referme l'écart
  entre le taux implicite de la grille et le taux publié par le COR à un
  dixième de point ; la ligne des cinq points capitalisés (point 5) l'était
  depuis la veille sans que la feuille le dise.

**Ce qui reste du volet A**, au 20 septembre 2026 : rien de ce que la liste
numérotait. L'assiette est certifiée et ses variantes calculables (points 1 et
4), les cotisants pondèrent la recette (point 3), les cinq points capitalisés
sont hors du bilan et la page le dit (point 5). Deux sources repérées en
chemin restent à certifier, chez le COR et dans le classeur que
`scripts/fetch/cor_comptes_retraite.py` télécharge déjà : la figure 3.1, taux
de cotisation d'un non-cadre du privé de 1940 à 2025 — c'est le contrôle
externe du rapport de recettes, cité de mémoire de lecture et non tenu par un
test — ; et le tableau 2.11, qui donne l'équivalence du COR entre un point de
taux de prélèvement et un pour-cent de masse de pension — 2,76 points contre
8,6 % à l'horizon 2070, sur le même champ que nos comptes. Le volet B est ce
qui reste de l'action.

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

*Le volet B est fait le 20 septembre 2026*, et voici comment les deux points
qui restaient ont été refermés.

**La garantie de la trajectoire est lue sur la distribution, et projetée
(point 1).** La ligne « dont garantie » des tableaux de la page Coût ne vient
plus des cas types. `GarantieDistribution`, dans `cout.py`, applique le barème
de `garantie.py` à la distribution de l'EIR 2020, année par année, et la
grille ne sert plus qu'à dire de combien cette distribution BOUGE : un seul
facteur, la pension moyenne que la garantie regarde (compte notionnel et rente
du pilier capitalisé, à partir de 65 ans, revalorisés) rapportée à la pension
moyenne du système actuel l'année de l'enquête, l'une et l'autre par tête et en
euros constants, lues sur la même grille. L'effectif suit les têtes de 65 ans
et plus de la grille, sur l'échelle des retraités de la DREES ; le plancher est
celui des paramètres, majoré puisque le foyer par défaut est une personne
seule. La forme de la distribution est tenue constante, le passé comme
l'avenir, et le même déplacement est appliqué à rebours avant 2020 : une seule
méthode sur toute la série, plutôt qu'une falaise entre deux. Porté dans
`moteur/js/cout.js` ; les lignes annuelles exposent `garantie` (facteur,
effectif, bénéficiaires, coût) et le dépliant de la page en montre cinq dates.

*Ce que ça déplace.* Le facteur vaut 0,64 en 2020 et 1,26 en 2070. La
trajectoire porte **1,30 % du PIB en 2026** (40 milliards d'euros de 2026,
6,8 millions de bénéficiaires) au lieu de 0,80 %, et **0,86 % en 2070**
(32 milliards, 5,1 millions) au lieu de 0,20 % : la grille voyait bien la
garantie s'éteindre, faute de queue basse, quand la distribution la voit
décroître sans s'annuler. Cumul 2025-2070 : 1 621 milliards constants au lieu
de 616. Le solde du scénario 6 ne bouge pas, la garantie étant financée par
l'impôt et comptée à part ; aucune pension ni aucun témoin de simulation ne
change. Le bogue du facteur de déplacement — la garantie retirée deux fois —
a été vu et corrigé le même jour par une autre session (note ci-dessous, dans
le volet A) ; le dépliant et le tableau poste par poste prennent désormais le
facteur DE LA TRAJECTOIRE, `garantie.facteur` de la ligne annuelle, qui compte
la rente capitalisée et les seuls 65 ans et plus, au lieu du rapport de masses
nu : 0,64 au lieu de 0,63 en 2020, et les deux lignes « pensions du système 4 »
du dépliant valent 30,0 et 53,7 milliards.

**Le net est sur la page, et les deux corrections sont sourcées (point 3).**
Le dépliant porte un tableau « ce que la garantie remplace » en 2024 : minimum
vieillesse 4,94 Md€ lus dans les comptes de la protection sociale, minimum
contributif 2,18 et minimum garanti 0,72 calculés sur la grille, pension
majorée de référence non chiffrée — 7,8 milliards, borne basse — contre
39,0 milliards de garantie la même année, soit **31 milliards de plus pour
l'impôt**, borne haute. Le non-recours et la récupération sur succession sont
lus et cités, non appliqués, parce qu'aucun des deux ne se transporte tel quel
dans le tableau : le premier vient du *Dossier de la DREES* n° 97 (mai 2022),
une personne seule éligible sur deux, 321 200 personnes fin 2016, 790 millions
non versés ; le second du rapport d'activité 2024 du FSV, 108,7 millions
récupérés en 2024. Les deux sont au manifeste des sources, `saisi`. *Le même
jour, plus tard* : le programme a tranché que la garantie se reprend sur la
succession, dès le premier euro et avec intérêts ; la note du dépliant, celle
de `limites.md` et le dépliant du programme ont été retournés en conséquence,
et ce que la reprise rendrait est l'objet de l'action 47.

*Ce qui reste une limite, et est écrit comme telle* : la forme de la
distribution est celle de 2020, déplacée sans être déformée ; le déplacement
est proportionnel et uniforme ; les retraités de moins de 65 ans, qui attendent
la garantie, sont supposés répartis comme les autres ; les deux minima de
pension sont calculés sur une grille qui n'est pas une population ; la pension
majorée de référence attend d'être portée au moteur (action 37).

Le point 1 et le point 3 tels qu'ils avaient été écrits sont ci-dessous, pour
mémoire.

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

**D. Le tableau poste par poste — `fait` le 20 septembre 2026.** Le bilan de
la page Coût ne se lisait qu'en deux courbes et un coefficient ; ce que chaque
décision de la proposition retire ou remplace, on le lisait dans une note. La
page porte désormais, sous « Recettes et dépenses, poste par poste », le
tableau 2.2 du rapport annuel du COR — la structure des ressources, en
milliards et en pourcentage du total — refait pour le système actuel et pour
la proposition, l'année de la bascule, avec les dépenses en face et le solde
en bas. `SoldeAnnuel.postes_ressources` et `postes_depenses` écrivent
`ressources_de` et `depense` ligne à ligne, au découpage du COR, et un test
tient que les lignes somment aux totaux pour les six systèmes et toutes les
années ; les « dont » de la ligne des transferts sont ce que la branche
famille et l'assurance chômage versent, celui de la ligne des impôts ce que
verse le fonds de solidarité vieillesse (`recette_non_acquise` prend un
`organisme`). Portage dans `moteur/js/cout.js` et `pages.js`, témoins
régénérés. En 2026, au PIB de 2025 : 417,7 Md€ de ressources pour le système
actuel (13,96 % du PIB) contre 236,9 pour la proposition (7,92 %), dont 228,9
de cotisations à 18 % ; 422,5 Md€ de dépenses (14,13 %) contre 276,9 (9,26 %) ;
un solde de −0,16 point de PIB contre −1,34. Pour mémoire et hors du compte,
la garantie vieillesse lue sur la distribution des pensions, 35,6 Md€ au
plancher de base, et le pilier capitalisé, 63,6 Md€. *Une chose vue en
chemin, corrigée le jour même* : le dépliant de la garantie déplaçait la
distribution du facteur `rapports["notionnel_liberal"] −
rapports[COMPOSANTE_GARANTIE]`, alors que depuis le 19 septembre la masse du
scénario 6 est déjà sa seule part contributive (`_pensionnes` y porte
`garantie_vieillesse.pension_contributive`, et le complément sous
`COMPOSANTE_GARANTIE`) — la soustraction retirait la garantie une seconde
fois. Le facteur est désormais `rapports["notionnel_liberal"]` tel quel, aux
deux endroits (`_cout_detail_garantie` et `_cout_detail_postes`, et leurs
jumelles en JavaScript). Ce que ça déplace, sur la distribution de l'EIR :
le facteur passe de 55 % à 63 % au réglage du programme, et le coût annuel de
la garantie aux pensions du système 4 de 35,6 à 30,5 Md€ au plancher de base
(47,6 % à 41,0 % des retraités, 7,9 à 6,8 millions), de 63,6 à 54,6 Md€ au
plancher majoré ; la ligne « pour mémoire » du tableau poste par poste suit,
de 1,19 à 1,02 % du PIB. Sur la variante des témoins qui indexe sur les prix,
bascule en 2030 et prend la cotisation totale, l'écart est plus grand parce
que la garantie y pèse plus : le facteur passe de 28 % à 43 %, et le coût de
73,7 à 47,0 Md€ au plancher de base. Le cumul de la garantie lu sur les cas
types, lui, ne bouge pas : il ne passait pas par ce facteur.

**Sources à lire.** INSEE, comptes nationaux annuels, salaires et traitements
bruts par branche (D11, niveau) et revenu mixte des entrepreneurs individuels ;
DREES, enquête annuelle auprès des caisses de retraite, effectifs de COTISANTS
par régime — et, lus le 20 septembre 2026, les projets annuels de performances
du PLF 2026, qui donnent un point par régime (SNCF 110 846 en 2023, RATP
39 956, ENIM 29 037 en 2024, mines 655, Opéra 1 879, Comédie-Française 352,
gérants de débits de tabac 25 078 en 2022) et le ratio cotisants/retraités
2012-2023 de la SNCF et de la RATP, saisis dans
`regimes/pap_regimes_subventionnes.csv` ; un appoint, pas une série ; COR, rapport annuel, taux de prélèvement global et assiette des
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

**Où l'action en est le 20 septembre 2026, face à cette fin.** Les quatre
lignes existent, réparties sur deux tableaux : le solde et le coefficient du
scénario 6 sont ceux des 18 % face à la répartition, et la garantie est la
ligne « dont… financée par l'impôt » de la trajectoire, avec son dépliant. Les
variantes de recette sont CALCULABLES (`convention_recette="rapport"`, et les
deux pondérations), mesurées et écrites dans `limites.md`, mais la page n'en
affiche qu'une, par la règle de l'action 40 : un réglage se voit ou n'existe
pas, et celui-là ne changerait rien à ce que le lecteur décide. `limites.md`
§5 ne dit plus que les recettes sont inertes. L'action est close ; ce qu'elle
laisse est écrit ci-dessus, volet par volet.

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
`origin/claude/clever-tesla-mln5zm` valait `670a258`, exactement `origin/main`.
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
(`main ← 670a258 (2 commit(s))`) quand il a poussé. Les poussées et le `fetch`
reprennent cinq fois, 2, 4, 8 puis 16 secondes, le réseau d'une session web
lâchant sans prévenir.

**Le cas qui s'est présenté pendant l'écriture même de ce script.** La
première version refusait toute divergence, comme la recette manuscrite et son
`--ff-only`. Elle a refusé de publier ce commit-ci : une autre session avait
poussé `6d2ad7d` entre le clone et la fin du travail, et les deux lignées
avaient chacune un commit depuis `670a258`. C'est le cas ORDINAIRE, et le
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

### 37. La cascade : ce que chaque mesure déplace, du scénario 1 au scénario 4 — `fait`

**La demande.** « Je veux faire un graphique de ce style dans la page des
coûts avec toutes les mesures que nous avons faites par rapport au scénario 1.
Il faut mettre le scénario 1, 422 milliards, à gauche et le scénario 4 à
droite. » Le modèle était une décomposition en cascade de la hausse des
dépenses publiques françaises, en points de PIB, fonction par fonction.

**Le diagnostic.** La page comparait bien les quatre systèmes, mais deux à
deux : un tableau disait de combien ils s'écartent, et jamais PAR QUOI. Pour
savoir laquelle des décisions du programme pèse, un lecteur devait soustraire
de tête quatre fois, et personne ne le fait. Les chiffres, eux, étaient tous
là : `masse_du_scenario` écrit la masse d'un système comme la part directe de
la base multipliée par son rapport, si bien qu'une différence de deux rapports
appliquée à la même part directe EST la contribution propre du changement qui
les sépare. Les marches sont donc exactement additives, et leur somme vaut
l'écart des deux totaux au centime.

**Ce qui a été fait.** `gabarit.cascade` et sa `Marche`, du SVG écrit à la
main comme le reste, portées dans `moteur/js/gabarit.js` et comparées
caractère par caractère par les témoins. Une barre rouge ajoute à la dépense,
une barre verte l'en retire, une barre grise est une mesure mesurée et nulle,
et les deux totaux portent la couleur de leur système. Les libellés sont posés
en biais à trente-cinq degrés : à l'horizontale, huit intitulés français ne
tiennent pas côte à côte. Le dépliant `cout-cascade` de la page Coût en pose
deux, et le docstring de `_cout_detail_cascade` dit pourquoi il en faut deux :
à l'année observée, la cotisation unique ne déplace rien, puisqu'elle ne vaut
que pour les droits acquis à compter de la bascule. Une cascade arrêtée là
montrerait la mesure centrale du programme à zéro sans rien dire.

**Ce que ça déplace.** En 2025, sur le compte du COR : 422,2 Md € de dépense,
−43,6 pour la réversion qui n'est plus servie, −270,5 pour le recalcul de la
part salariale, +153,3 pour la part patronale portée au compte, 0,0 pour la
cotisation unique, +21,6 pour la garantie vieillesse, soit 283,0 Md €. À
l'horizon 2070, sur la trajectoire du modèle et en euros constants : 714,2
−40,5 −461,6 +262,9 −103,8 +17,7 −8,5 = 380,5 Md €. Les deux jeux de chiffres
étaient déjà dans les tableaux de la page ; c'est le chemin qui ne l'était pas.

**Ce qui le tient.** Trois entrées au catalogue des affirmations, avec leurs
contrôles : `cascade_somme_exactement` refait la somme sur les deux lectures
et vérifie que l'ordre des marches ne change pas le total,
`cascade_cotisation_unique_sans_effet_avant_la_bascule` tient les deux bouts
de la marche nulle, `cascade_ne_porte_que_la_depense` vérifie qu'aucune
recette n'y entre. Et `test_aucun_graphique_n_est_livre_sans_ses_chiffres`
compte désormais deux familles : un tableau de cascade ne peut plus couvrir un
tracé de courbe manquant.

**Ce que ça ne fait pas.** Une décomposition séquentielle : chaque marche est
l'effet de sa mesure sachant les précédentes, et la page l'écrit. Et une
dépense n'est pas un solde : la cascade ne montre qu'un côté du compte, ce que
la dernière note dit en renvoyant au dépliant des postes.

### 38. La cascade devient dynamique : elle se tient à jour, se survole, et son année se choisit — `fait`

**La demande.** « J'aimerais que ce graphique soit dynamique. En effet,
beaucoup de choses changent souvent et c'est pas évident de tout mettre à jour
car le site commence à devenir énorme. » Trois choses sous un seul mot, et
l'utilisateur les a toutes retenues : qu'elle se tienne à jour seule, qu'elle
réagisse au survol, et qu'on y choisisse l'année.

**Ce qui était figé.** Tous les chiffres de la cascade venaient déjà du
modèle ; trois choses ne venaient de nulle part. La CHAÎNE des systèmes était
recopiée à la main, en double de `SCENARIOS_MONTRES`. L'étiquette écrivait
« Cotisation unique de 18 % » quand le taux est un réglage que l'adresse porte,
et une glose « un dixième de la masse versée » quand cette part tombe à 5,7 %
en 2070. Les reprises sur successions entraient comme un MONTANT emprunté à la
trajectoire, seul endroit de la page où un niveau traversait d'une série à
l'autre.

**Ce qui a été fait, et ce que ça retire.** La chaîne se déduit de
`SCENARIOS_MONTRES` ; `MARCHES_SYSTEMES` ne fait plus que nommer. Les étiquettes
portent des accolades, remplies à l'année et sous les réglages. Les reprises
passent par une fraction de ce que la garantie a versé — un rapport, comme tout
ce que cette page emprunte au modèle.

Et surtout : **il n'y a plus qu'une cascade là où il y en avait deux.** La
seconde existait parce qu'à l'année mesurée la cotisation unique ne déplace
rien, n'ayant pas encore de droits acquis sous elle ; elle était prise sur la
trajectoire du modèle, donc sur un autre périmètre et une autre unité, ce qui
demandait un paragraphe pour prévenir qu'on ne pouvait pas les soustraire. Le
compte du COR tient en réalité ses deux bouts de 2002 à 2070 : seul l'euro lui
manque au-delà de l'année publiée, et le modèle en projette un qui coïncide
exactement avec le sien à l'année de jonction. Un sélecteur d'année suffit donc,
sur un seul périmètre, et le paragraphe de mise en garde disparaît avec la
seconde figure.

**Une vue n'est pas un réglage**, et `_VUES_DE_PAGE` porte la distinction. Un
réglage change le modèle et voyage vers toutes les pages ; une vue choisit ce
qu'on montre, ne change aucun chiffre, et ne vaut que pour sa page. L'année de
la cascade est une vue : elle n'entre donc pas dans `Saisie`, où elle aurait
voyagé jusqu'à Cas types et Avantages, qui n'en ont rien à faire. Elle survit en
revanche au bouton « Recalculer cette page », en champ caché, comme les deux
réglages sans champ.

**Le survol** suit le contrat des courbes : les chiffres viennent du tableau
posé sous la figure et de nulle part ailleurs. Ce qui change est la façon de
viser — une cascade n'a pas d'abscisse continue mais des colonnes, et l'on
cherche la barre dont le centre est le plus proche du pointeur, en coordonnées
d'écran plutôt qu'en rejouant l'échelle du `viewBox`, ce qui tient dans une
boîte qui défile. Flèches et Échap au clavier, lecture en région `aria-live`.

**Ce qui le tient.** `test_la_cascade_suit_la_liste_des_systemes` tient les deux
listes face à face : un système entré au site sans son nom fait tomber le test,
plutôt que sortir une cascade à qui il manque une marche — laquelle sommerait
encore juste, ce qui est le pire des cas.
`test_aucune_etiquette_de_cascade_n_ecrit_un_nombre_en_dur` refuse le moindre
chiffre dans un gabarit d'étiquette. Deux témoins de plus comparent les deux
portages sur les branches du sélecteur que le défaut ne visite pas : l'horizon,
où le PIB est projeté et où toutes les mesures mordent, et une année hors liste,
qui doit retomber sur l'année mesurée des deux côtés. Et
`test_une_page_agregee_au_defaut_ne_dit_rien_des_reglages` vérifie désormais ce
qu'il voulait dire : un lien peut porter une vue, jamais un réglage que le
lecteur n'a pas demandé.

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

- **20 septembre 2026, parcours de présentation.** Une présentation du site
  à 13 h 30 le jour même, par quelqu'un qui ne l'avait pas vu. La version
  publiée sur GitHub Pages était identique à `main`, sans erreur sur les neuf
  onglets, la suite verte ; la copie sous `partiliberalfrancais.fr/retraite/`
  datait du 19 au matin, cinquante commits en arrière, sans le pilier
  capitalisé. `docs/parcours_presentation.md` dit dans quel ordre montrer les
  pages, ce que l'exemple pré-rempli et trois carrières adressées donnaient ce
  matin-là, et les questions à attendre avec la page qui y répond. Déclaré
  `recit` dans `zones.yaml` : ses chiffres sont ceux d'un matin.
- **20 septembre 2026, action 44.** Faite. La page Coût dit quelle part de
  la dépense n'a été cotisée par personne : une note de quarante mots en haut,
  qui porte son propre total et renvoie à la page Avantages, et un tableau par
  famille dans le dépliant des dépenses, sur le seul total où la part soit
  juste, celui de la DREES. Aucun graphique de plus, rien dans le modèle. Le
  détail est sous l'action.

- **20 septembre 2026, action 56.** Faite. Le risque de défaut du système
  actuel, premier argument de la proposition, n'avait pas de page. Quatre
  revues de littérature (théorie et dette implicite ; projections
  françaises ; défauts observés ; risque comparé et perception), une page
  `Risque` en deux cartes et dix dépliants, un document `docs/risque_de_defaut.md`
  qui porte l'état de l'art avec ce qui a été lu et ce qui ne l'a pas été.
  Ce qu'il faut en retenir : la recherche ne connaît aucune probabilité de
  défaut, et le dire est son premier résultat ; le seul chiffre que la page
  calcule est celui que le modèle lit déjà dans les comptes du COR, et il dit
  la taille de l'ajustement à venir, pas sa forme.

- **21 septembre 2026, action 59.** Faite. La page Risque cesse d'être une
  revue équilibrée pour devenir le réquisitoire qu'elle devait être, à la
  demande. Trois choses à en retenir. **Le meilleur argument contre le système
  est écrit par le COR** : c'est lui qui dit que financer la promesse par les
  cotisations est récessif et prend l'argent de l'école et de l'hôpital, et
  une citation institutionnelle ne se récuse pas comme partisane. **La part
  patronale est du salaire**, et c'est démontré précisément pour la retraite,
  parce que c'est la cotisation la plus contributive du barème. Et **garder
  les contre-arguments renforce la page** : les trois résultats qui
  contredisent la thèse générationnelle y sont cités, ce qui ôte à un
  contradicteur son seul angle d'attaque.

### 37. Chiffrer les avantages non contributifs, et les montrer — `fait`

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

**Ce que ça a déplacé.** Le chiffrage des avantages non contributifs est passé
de **5,3 milliards, soit 1,2 % de la dépense**, à **95,2 milliards, soit
22,3 %** — le COR chiffre les droits de solidarité à « de l'ordre d'un
cinquième », et on y est. L'inventaire compte quarante-deux dispositifs, dont
dix-huit portent un chiffre et vingt-quatre une raison écrite, et **aucun ne
porte plus la mention « à certifier »** : les quarante-deux ont leur base légale
lue dans LEGI, version par version. Le site a une page qui les nomme tous.

Le chemin importe plus que le chiffre d'arrivée, et il tient en une phrase :
**86 % du total est LU, non calculé.** Ce que le modèle apporte n'est pas le
montant, c'est la LISTE et l'article sous lequel chercher. Les deux découvertes
qui ont fait le gros du trajet sont de la même famille : les comptes de la
protection sociale ventilent le risque vieillesse-survie en sous-postes depuis
2020, et le jaune budgétaire détaille la fonction publique — deux publications
que l'inventaire ignorait parce qu'il avait été bâti depuis les listes du
dépôt, qui disent ce que le MODÈLE sait faire, au lieu de la nomenclature des
producteurs, qui dit ce que le SYSTÈME verse. C'est la seconde qui fait foi sur
l'exhaustivité, et c'est la leçon transposable de cette action.

**Ce qui reste, et pourquoi ça reste.** Vingt-quatre dispositifs sans chiffre,
en quatre tas de nature différente :

- **cinq ne pourront jamais en avoir.** Deux ne paient qu'à compter de 2026
  (surcote parentale, salaire de référence des parents) ; trois ne sont pas des
  dispositifs mais des écarts de règle, mesurés ailleurs — la décote non
  actuarielle au §4 ter, le rendement au scénario 2, le financement par l'impôt
  dans les recettes.
- **cinq attendent que le producteur les sépare** d'un poste fourre-tout :
  l'allocation veuvage, la majoration forfaitaire de réversion, les points
  gratuits de complémentaire, le service national, et la part vieillesse du
  fonds amiante, que son compte mêle à l'allocation.
- **cinq sont dénombrées mais pas valorisées** : les bonifications de service,
  dont le jaune donne les bénéficiaires et les trimestres, et un ordre de
  grandeur de 4,3 Md€ pour l'État qui croise deux millésimes et n'entre donc pas
  dans le total.
- **neuf attendent une saisie que le simulateur ne fait pas** — un taux
  d'incapacité, un corps d'appartenance, une durée de congé parental. Elles ne
  coûtent pas une source mais un champ de formulaire, et chacune élargirait la
  saisie pour une population étroite.

Une chose reste franchement ouverte et n'est bloquée par rien : **porter la
décomposition sur la page Coût**. L'objection qui la retenait — elle mesurait
1,2 % de ce qu'elle prétend mesurer — est levée. Reste à décider si la page Coût
reprend la décomposition ou se contente d'y renvoyer. C'est l'action 44.

**Ce qui restait à l'ouverture, dans l'ordre du gain.**

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

**Volet J — les projets annuels de performances du PLF 2026, lus : la masse
des bonifications des régimes spéciaux, en trimestres.** Le 20 septembre 2026,
sur sept annexes budgétaires apportées par l'utilisateur (programmes 195, 197,
198, 741, 743, 148 et le document de mission) — aucune n'avait été prise en
compte, et le dépôt ne sait pas les récupérer.

- *Ce que le programme 198 publie, et que personne d'autre ne publiait.* Sur
  le flux de nouveaux pensionnés, de 2012 à 2023, les trimestres COTISÉS et
  VALIDÉS de la RATP — 125,2 contre 168,5 en 2023, soit 43 trimestres que la
  pension rémunère sans cotisation, ratio stable à 0,74-0,76 — et les années
  cotisées et validées de la SNCF, 37,66 contre 38,05, en disant que les
  validées « comprennent les bonifications propres au régime ». L'écart de la
  RATP mêle les bonifications de services, d'enfants, de campagne et les
  périodes validées sans cotisation ; le PAP ne les sépare pas. Celui de la
  SNCF est petit parce que la bonification de conduite ne va qu'aux
  conducteurs et que le flux mêle tous les agents.
- *Une ligne d'inventaire de plus, la quarante-troisième, et elle manquait.*
  Les fiches de la SNCF et de la RATP déclarent le code `bonifications` depuis
  toujours, mais le moteur le lit comme la bonification pour ENFANTS de la
  fonction publique (`actuel.py`) : les bonifications de SERVICES de ces deux
  régimes n'étaient ni servies ni inventoriées. `bonifications_regimes_speciaux`
  les porte, `absent`, fondée sur deux articles lus dans l'index LEGI —
  l'article 9 du décret n° 2008-639 (SNCF : un trimestre par année de
  conduite au-delà de la troisième, vingt au plus) et l'article 20 du décret
  n° 2008-637 (RATP : un cinquième des services du tableau B, cinq ans au
  plus), agents admis avant 2009 dans les deux cas.
- *Ce qui ne se convertit pas.* En euros, il faudrait une valeur du trimestre
  par régime et par génération : même refus qu'au volet I. Les chiffres sont
  saisis, page par page, dans `regimes/pap_regimes_subventionnes.csv`, avec
  ce que les mêmes documents donnent aux actions 2, 14 et 35 et le schéma de
  financement de 2025 (`docs/regimes.md`).

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

Le 20 septembre 2026, l'APEC est sortie des prélèvements que la proposition
remplace : l'Agirc-Arrco la recouvre avec la CEG et la CET, mais elle finance
le service de l'emploi des cadres, pas la retraite, et un scénario qui change la
retraite la laisse en place, comme le chômage ou la maladie. La proposition ne
retire donc que ce qu'elle remplace — CNAV, Agirc-Arrco, CEG, CET —, et rien
d'autre : maladie, famille, AT-MP, autonomie, chômage, AGS, FNAL, dialogue
social, CSG et CRDS restent sur la fiche. L'effet est de 65 € par an pour un
cadre à deux fois et demie le salaire moyen.

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

### 41. Tarir la prose périmée, au lieu de la réparer un chiffre à la fois — `fait`

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

**Le 21 septembre 2026 : le cliquet passe de 192 à 73.** Une passe d'arbitrage,
document par document, et trois choses qu'elle a trouvées.

*Le partage de `limites.md` était le morceau annoncé, et il s'est fait d'un
seul mouvement.* Quarante-six sections y racontent une correction datée — un
AVANT, un APRÈS, la fiche ou la table qui a changé ce jour-là — et c'est le
critère qui les range en `recit` : les rafraîchir effacerait ce qui a été
corrigé. Sept autres disent ce qui est vrai aujourd'hui sans porter un seul
chiffre nu, et passent en `etat`. Ce qui reste attend une sonde par chiffre,
et c'est là qu'est désormais le travail : le §1 et son état de certification,
le §5 et ses réserves, la trajectoire projetée.

*Les autres documents se rangent par leur usage, pas par leur temps.* Ce qui
est écrit pour être SUIVI est `etat` de bout en bout, parce qu'une consigne
périmée se suit quand même : `CLAUDE.md`, la remise au mainteneur du site
d'accueil, la procédure de veille. Les deux procès-verbaux enclavés dans
`CLAUDE.md` — l'audit des quatorze branches, le compte des recalculs de
`date_liquidation` — sont gelés par `paragraphes_recit`, mécanique que la
feuille de route avait déjà pour ses bilans. Vingt et une sections de
`methodologie.md` et sept du README suivent, sans un chiffre à ancrer.

*Quatre chiffres ont été pris en flagrant délit, et aucun n'aurait été vu
autrement.* La remise au mainteneur annonçait un paquet de données de 2,9 Mo
bruts et 310 Ko compressés, pour 3 049 et 346 ; `veille_droit.md` disait
« vingt-deux exemples publiés » dans une section intitulée « aujourd'hui »,
pour 21 ; `methodologie.md` donnait « cent vingt jeux de données des
vingt-huit institutions », pour 161 et 36 ; le tableau des avantages non
contributifs comptait 20 dispositifs `absent` pour 21. Les quatre étaient
écrits en toutes lettres ou sans unité — c'est-à-dire exactement là où le
contrôle ne regarde pas. Ils sont maintenant ancrés, donc recalculés.

**Deux outils en sont sortis.** Le découpage en sections prenait un `#` de
bloc de code pour un titre : les commentaires des exemples Python du README en
ouvraient onze, qui gonflaient le cliquet et, plus grave, coupaient en deux la
section réelle qui les contient — un régime déclaré sur elle ne valait plus
que jusqu'au premier commentaire. Et une sonde qui compte peut maintenant
traverser un cran d'entrées : `entrees(data/sources.yaml:institutions.*.jeux)`
réunit les jeux de toutes les institutions, que rien ne totalisait ailleurs.

**Le 21 septembre 2026, plus tard : les paramètres de droit lisent leur
table.** Le recensement des paramètres du scénario 1 — l'étalon du dépôt —
portait vingt-six chiffres recopiés à la main depuis les tables certifiées,
faute d'une sonde qui sache descendre dans un CSV. Quatre sondes le font
maintenant : `cellule` pour une ligne désignée par ses clés, `minimum` et
`maximum` pour les bornes d'une colonne, `distinctes` pour le nombre de
valeurs différentes. Une colonne porte au besoin son changement d'unité —
`coefficient*100` lit en pour-cent la fraction que le fichier stocke,
`valeur/12` dit au mois un montant annuel. Une cinquième, `partout`, rend la
valeur que toutes les entrées désignées portent et refuse dès que deux
s'écartent : c'est exactement ce qu'affirme une prose qui annonce un nombre
unique, et c'est ainsi que le plafond de la majoration familiale de
l'Agirc-Arrco est tenu.

Le tableau du scénario 1 est donc entièrement ancré, et deux chiffres seulement
ne viennent pas d'un fichier : l'assiette de l'AVPF et l'âge majoré de la
surcote de 2007-2008 sont des constantes du moteur, que `tenu()` renvoie à un
test nommé — le second a été écrit pour cela, parce que la table porte le
drapeau `apres_65_ans` et jamais l'âge lui-même. Un troisième, l'écart de
4,6 % entre le minimum garanti servi en 2024 et sa projection sur les prix,
demandait de chaîner vingt années d'indice : c'est un test qui le tient, et il
échouera le jour où l'écart bougera.

**Et le lecteur de nombres avait un trou.** « 7 603,41 » se lisait comme DEUX
nombres, 7 603 et 41 : le motif ne prévoyait pas la décimale après le
séparateur de milliers. L'ancre refusait donc tout montant de cette forme, et
une correction automatique en aurait fait « 7 603 ».

**Le §1 ne se produira pas : il se lit.** Le chantier annoncé était d'écrire
son tableau depuis les données, comme `construire_regimes_md.py` écrit
`regimes.md` depuis l'inventaire. La mesure l'a réfuté : sur les 95 lignes du
tableau, **onze seulement** portent une source que le journal de certification
porte au caractère près, et les périodes qu'il donne sont éditoriales — « ancres
2007, 2016, 2017, depuis 2021 », « avant 1934 à 1948 », « le reste de
1931-2001 ». Produire ce tableau ne serait pas le dériver, ce serait recopier
sa prose dans un YAML : le même texte, ailleurs, plus une couche à tenir.

Ce qui se dérive vraiment, ce sont les BORNES. **Trente et une lignes lisent
maintenant leur période dans le fichier qu'elles décrivent**, par les sondes de
l'étape précédente : `minimum(ipc_annuel.csv:annee?fiabilite=certifiee)` et son
`maximum`. C'est la dérive la plus probable de ce tableau — une série
s'allonge d'une année et la prose reste à l'ancienne —, et elle s'est produite
sous la main : la complémentaire agricole était donnée certifiée jusqu'en 2024,
le fichier porte 2025.

Un test lie les deux colonnes, qui se modifient séparément : la période d'une
ligne est lue sous un filtre de fiabilité, et la colonne « Niveau » doit dire
ce niveau-là. Sans lui, une ligne pourrait annoncer « certifiée » en lisant les
bornes des années estimées.

**Deux choses trouvées en chemin, et corrigées le jour même.**

*Le compte des institutions était écrit en dur, « 28 », dans les deux
portages* — `pages.py` et `pages.js` —, quand `sources.yaml` en porte 36. Le
même chiffre était faux dans `methodologie.md`, en toutes lettres, et dans le
parcours de présentation. Il se lit maintenant là où il vit :
`compter_institutions()` pour le Python, et le paquet de données pour le
JavaScript, que `construire_donnees.py` remplit de la même valeur. Un seul
endroit peut désormais le faire dériver, et c'est le manifeste lui-même.

*Le tableau de certification donnait « fausses » les taux du régime général de
1980 et 1981* — le décret n° 79-650 du 30 juillet 1979 les a relevés « à titre
exceptionnel » sur une fenêtre qui couvre deux 1er janvier, et ni l'IPP ni
OpenFisca ne portent la hausse — quand `taux_cotisation_annuels.csv` les porte
`haute`, au niveau de leurs voisines. **La recherche que personne n'avait faite
a tranché, et dans l'autre sens : ces taux sont justes.** Le décret est le point
exceptionnel du plan Barrot, porté par la seule cotisation MALADIE du salarié —
3,50 % puis 4,50 % au 1er août 1979, ramenée à 4,50 % au 1er février 1981,
dix-huit mois plus tard —, et le recueil statistique de la Cnav écrit que la
vieillesse plafonnée vaut 12,90 % du 1er janvier 1979 au 1er janvier 1984, sans
marche entre-temps. LEGI le confirme par son silence : dans le décret
n° 67-803, les articles de la maladie ont une version qui s'ouvre au 1er janvier
1980, seconde fenêtre du texte, et celui de la vieillesse n'en a aucune. Le
décret rejoint la liste des textes que la série ignore à bon droit, avec sa
raison : sur 1967-1981, plus un seul décret de taux du régime général n'est
inexpliqué.

*Et la leçon vaut mieux que le chiffre.* Le contrôle qui avait trouvé ce décret
était juste ; c'est la conclusion qu'on en tirait qui ne l'était pas, et elle
avait été recopiée dans quatre fichiers — le tableau de `limites.md`, le
manifeste des sources, le récupérateur et le vérificateur. « Un décret que la
série ignore » ne veut pas dire « les années qu'il couvre sont fausses », mais
« personne n'a encore dit ce que ce texte leur fait ». Le message du contrôle
disait la première phrase ; il dit maintenant la seconde.

**Le 22 septembre 2026 : ce que le modèle calcule cesse d'être recopié.** Le
tableau des règles d'indexation — les neuf rendements cumulés de 1941 à 2025,
qui portent l'argument principal du dépôt — existait en TROIS exemplaires : le
site le calcule à chaque rendu, le README et la méthodologie le recopiaient. La
page avait déjà payé cette dette une fois, ses neuf nombres y étant écrits en
dur, et l'un d'eux mentait de trois dixièmes de point ; les deux copies de la
prose étaient restées dans cet état, et elles donnaient le PIB nominal à
1 068,6 % quand le modèle en calcule 1 068,3.

`scripts/construire_tableaux_md.py` les écrit maintenant entre deux repères,
depuis `_cumuls_indexation` — la fonction même du site —, et un test refuse une
prose qui ne serait plus la sienne. C'est le geste de `construire_regimes_md.py`
pour `docs/regimes.md`, appliqué à un BLOC au lieu d'un document entier : un
`blocs_produits` dans `zones.yaml` exempte ces lignes de l'ancre par cellule,
puisqu'un script les écrit et qu'un test les tient. C'est la quatrième forme du
régime `produit`, et celle qui manquait — un document mêle la prose et ce qui
se calcule, et il fallait pouvoir le dire ligne à ligne.

Le second tableau du §1 a suivi le même chemin : les cinq générations qui
mesurent ce que la correction de la ligne de référence déplace — le scénario
rétroactif sous les prix, puis sous la revalorisation réellement portée au
compte. Cinq simulations, une seconde et demie, et l'écart de la génération
1920 passe de +5,2 à +5,0 points : le tableau avait vieilli d'un point sur ses
deux premières lignes, non parce qu'on l'avait mal écrit, mais parce que le
modèle a bougé sous lui. C'est la forme la plus discrète de la péremption, et
la seule qu'aucune relecture n'attrape.

**Ce qui reste — et c'est le travail, qui se fait section par section.**
Soixante-douze sections, et elles ont toutes la même forme : elles disent ce
que les chiffres du dépôt valent AUJOURD'HUI, et chacun de leurs chiffres est
une mesure du modèle — un écart en pourcentage, un montant, une part de PIB.
Aucune ne se déclare sans une sonde qui la recalcule, ou sans un test nommé
qui la tienne déjà — et les sondes de table n'y suffisent pas, puisque ces
chiffres-là ne sont dans aucune table. Le §1 de `limites.md` en porte à lui
seul deux cents, et c'est le plus gros morceau qui reste ; les six résultats du README et les
sections chiffrées de `methodologie.md` suivent. Une seule phrase bloque le §2
de `avantages_non_contributifs.md` : les 87 % du total chiffré que les lignes
lues font, part qu'aucune sonde ne recalcule et qu'aucun test ne tient. Rien
n'oblige à tout reprendre d'un coup, et rien ne permet de reculer.

**Le 22 septembre 2026 : les gains faciles sont épuisés, et trois sections
butent sur autre chose.** Une passe de mesure sur les soixante-douze sections
restantes : AUCUNE ne passerait en `etat` sans poser une ancre. Les sept
sections que la passe du 21 septembre avait trouvées sans un seul chiffre nu
étaient les dernières de cette espèce ; ce qui reste demande une sonde par
chiffre, une à une, et c'est le travail annoncé.

Trois d'entre elles butent sur un obstacle d'une autre nature, et il valait
mieux le nommer que le redécouvrir : les sections de `docs/outillage_interface.md`
n'affirment rien sur le dépôt mais sur des ARTEFACTS EXTÉRIEURS — le moteur
Impeccable pèse 16 Mo, Chromium 190, le hook tourne par défaut à 8 000
caractères. Aucune sonde ne peut recalculer le poids du binaire de quelqu'un
d'autre ; `illustration()` ne convient pas, puisque ces nombres peuvent devenir
faux ; et payer la dette `a_verifier` est interdit par le cliquet, qui ne peut
que décroître. Ces trois sections resteront donc `a_declarer` tant que les
poids y figureront, et c'est la mécanique qui fonctionne, non une dette oubliée.

**Ce qui pouvait l'être y a été tenu quand même.** Le même document cite trois
versions figées — la compétence Impeccable, son moteur, le CLI Playwright —, et
le dépôt les porte toutes les trois : l'en-tête de `SKILL.md`, le fichier
`scripts/VERSION`, la variable `PLAYWRIGHT_CLI_VERSION` de
`scripts/setup_ui_tools.sh`. Le contrôle par ancre ne les voit pas — « 0.1.20 »
n'est pas un chiffre au sens de son motif —, et une prose qui cite une version
pendant que le script en installe une autre se serait séparée sans bruit.
`test_l_outillage_annonce_les_versions_qu_il_installe` les lie désormais aux
cinq endroits où le document les écrit.

**Le 22 septembre 2026, au soir : douze sections de la méthodologie, et
trois chiffres que le modèle avait laissés derrière lui.** Le cliquet passe de
66 à 54. Quatre mesures rejoignent le registre de `scripts/mesures_prose.py` —
`taux_indexation` (ce qu'une règle accorde une seule année), `anticipation`
(le coût d'un départ anticipé à capital donné, qui suit l'âge de référence
quand il bouge), `millieme_salaire`, `poids_trimestre` —, et `constante` lit
désormais une constante de classe ou l'élément d'un couple.

Ce que l'ancrage a trouvé : le lissage donnait −81,5, −80,2 et −79,1 % à la
génération 1930 quand le modèle en calcule −83,9, −82,9 et −81,9 ; le régime
unique répartissait 25,73 % quand il applique 25,83 — la même dérive que le
README, dans une seconde copie ; et l'exemple du compte « revalorisé de 1 à
5 % quand les prix montent de 10 à 50 % » ne tenait pas, l'après-guerre ayant
revalorisé de 14 % pour 52 % d'inflation. Il cite maintenant deux années
réelles, 1946 et 1981.

Ce qui reste dans ce document est plus lourd : la construction des scénarios 6
et du pilier capitalisé, la contribution employeur du public, les tables de
mortalité — chacun une vingtaine de chiffres ou plus. Et *Le périmètre du taux
de cotisation* attend une mesure qui somme les taux d'un statut une année
donnée : son 25,7 % de 2023 n'est dans aucune fiche seule.

**Le 22 septembre 2026, dans la nuit : le README et `limites.md` entièrement
déclarés, et la sonde qui lit le modèle.** Ce qui restait disait ce que le
MODÈLE calcule — un écart de pension, un coût, un solde —, et aucune sonde ne
savait le lire. `mesure(nom?clé=valeur)` le fait, adossée au registre de
`scripts/mesures_prose.py` : écart d'un scénario sur une carrière nommée,
rendement cumulé d'une règle, coût, part de PIB, solde, coefficient,
dette, garantie, avantages, fiche de paie, paramètres et constantes. Chaque
mesure est mémorisée pour le processus, et le coût agrégé ne se calcule
qu'une fois ; la vérification de la prose en coûte une trentaine de secondes
de plus. Les deux sorties d'exemple du README, collées à la main, sont
écrites par `construire_tableaux_md.py`.

*Ce que l'ancrage a trouvé*, et c'est l'argument de l'action : presque aucune
section chiffrée ne disait plus le vrai. Le README donnait la garantie
vieillesse à 40 milliards en 2026 pour 17,8, le système actuel à 19,3 % du PIB
en 2070 pour 18,4, le COR à 14,2 % pour 15,3, le solde du scénario 6 en 2050 à
−2,03 points pour −1,65, sa dette à 103 % du PIB pour 84, le taux du régime
unique à 25,73 % pour 25,83, la part salariale du régime général à 40,87 %
pour 44,66, 36 réformes au calendrier pour 89 ; il affirmait que le scénario 3
n'économise rien en 2026, quand il y cesse de servir la réversion, et que la
garantie fait partie du total du 6, quand elle s'y ajoute. `limites.md` faisait
passer un fonctionnaire d'État à +4,5 % au scénario 4 pour +35,3, lisait la
recette du 6 par un rapport de taux abandonné, et donnait au solde de ce
scénario −2,16 % du PIB pour −1,22. Trois phrases étaient fausses sans chiffre
en cause : la masse salariale « de très loin la plus généreuse » des règles,
que le PIB lissé dépasse ; « la moitié de l'écart est de la rétroactivité »,
qui en est l'essentiel ; et le simulateur qui « ne propose pas » la saisie en
net, quand il la propose.

*Ce qui ne se recalculait pas n'est plus chiffré*, plutôt que d'être avoué :
une douzaine de nombres qu'aucune mesure ne rend — la sur-revalorisation de
12,1 %, le « +39 € une fois le brut stabilisé », le 8 % de rente du frais de
réserve — sont redevenus des phrases. Les citations de sources datées (CNAV,
CEPII, OPEF, barèmes de 2026) sont des `illustration()`.

*Les chroniques ont reçu un intertitre.* Cinq sections de `limites.md`
mêlaient l'état et le journal des corrections qui y avaient mené ; le journal
a désormais son intertitre, déclaré `recit` — l'enquête sur les coefficients de
revalorisation, le registre des recontrôles, les décisions du 19 septembre sur
la recette du 6, l'écart au COR, les mesures de la garantie —, et l'état est
ancré au-dessus. Quatre outils du contrôle ont été réparés en chemin :
`--corriger` réécrivait l'argument de l'ancre quand le nombre y figurait ; le
lecteur ignorait l'espace fine comme séparateur de milliers ; un signe
typographique n'était pas gardé à la correction ; un paragraphe en retrait
échappait au gel.

**Le 23 septembre 2026, dans la nuit : la méthodologie, section par
section.** Dix-sept sections y sont passées en `etat` depuis la note du soir,
et douze mesures ont rejoint le registre — la fusion sous une autre règle,
l'âge de référence, les droits acquis sous les deux conventions, les
populations de mortalité, la fourchette du site, les fiches telles qu'elles
sont écrites. La méthodologie était le document le plus en retard du dépôt,
parce qu'elle décrit le modèle et que le modèle avait bougé sous elle :

- *le régime unique* ouvrait à 64 ans et donnait le taux plein à 67, pour
  65 et 67,5 ; son taux le plus élevé était « la tranche 2 de l'Agirc-Arrco,
  21,59 % », quand c'est une caisse publique d'équilibre à 41,2 % ;
- *la part salariale des fiches* avait quatre points de retard pour le
  régime général (40,87 % pour 44,66), et la tranche 2 de l'Ircantec n'a
  jamais été à 40 % ;
- *les tables de mortalité* ignoraient Vallin et Meslé, et faisaient
  reconstituer par la loi paramétrique toute la mortalité d'avant 1986 ;
- *l'âge de référence* atteignait 64 ans « en 2030 » : la suspension de la
  loi n° 2025-1403 le reporte à la génération 1969 ;
- *les droits acquis* donnaient leur exemple sous un âge de référence de
  67 ans, qui n'est plus le défaut, et leurs quatre montants avaient bougé ;
- *le taux d'appel* restait à 125 % « depuis 1995 », pour 127 % depuis 2019 ;
  la sur-revalorisation de l'ancienne approximation vaut 17,4 %, pas 12,1 —
  elle est de nouveau chiffrée, par une mesure qui la recalcule ;
- *la décote de 2012* s'annulait « à 63 ans », pour 63 ans et neuf mois ;
- *la section sur 1980 et 1981* les tenait encore pour fausses, cinquième
  copie de l'erreur que la recherche du 21 septembre avait réfutée.

Deux affirmations se contredisaient dans la même section — l'emploi projeté
« sur la trajectoire du COR par défaut », puis « supposé constant » —, et le
fichier d'hypothèses a tranché. Une troisième ne se vérifie plus : la
reconstruction d'une colonne de revalorisation depuis sa voisine « divise la
dérive par dix » ; le test qui la mesure trouve 0,12 % contre 0,26 %, un
rapport de deux. La méthodologie renvoie désormais au tableau de
`limites.md` sans recopier ses chiffres, mais ce tableau, la docstring de
`coefficient_revalorisation_portee_au_compte` et celle du test disent encore
« par dix » : c'est à reprendre avec la définition exacte de la mesure.

**Ce qui reste.** Trois sections de la méthodologie — le scénario 6, le
pilier capitalisé, le solde —, laissées à la session qui tient la recette et
la garantie de ce scénario, et les trois de `docs/outillage_interface.md`,
qui restent `a_declarer` pour la raison dite plus haut.

**L'angle mort à traiter ensuite.** Ce contrôle ne juge pas une phrase,
seulement un nombre : « la bascule ne reprend aucun droit acquis » lui est
invisible. C'est l'action 34, et les deux se complètent — l'une tient les
chiffres du dépôt, l'autre les affirmations du site.

**Le 23 septembre 2026 : les deux cliquets à zéro, et l'action close.** Six
sections restaient à déclarer et deux chiffres portaient l'aveu `a_verifier` ;
il n'en reste aucun. Quatre passes, poussées une à une.

*Les trois sections de la méthodologie* — le scénario 6, le pilier capitalisé,
le solde — portaient quatre-vingt-douze chiffres nus, et l'ancrage a trouvé ce
que la relecture ne voyait plus. Le coefficient d'équilibre du scénario 3 en
2070 était écrit 1,87 et l'économie qu'on lirait à tort 46 %, pour 1,67 et 40 %
à l'ancrage, puis 1,71 et 41 % une heure plus tard. L'État verse 82,28 points pour ses
fonctionnaires en 2026, et le texte disait « soixante-dix ». La recette que les
scénarios notionnels ne peuvent pas compter y était donnée pour 3,7 % des
ressources : c'est la part de la CNAF et de l'Unédic, et le modèle retire aussi
celle du FSV, 8,5 % en tout. La carrière des tests d'allocation verse 31 ans,
pas 36. La garantie y restait « financée par l'impôt », sans la reprise sur
succession ni le recours d'un ayant droit sur deux que l'action 47 y a mis.
Et la colonne « ASPA actuelle » du tableau des couples appliquait en fait au
foyer les planchers de la garantie : elle le dit, à côté de l'ASPA de 2026
lue dans sa table. Quatre mesures ont rejoint le registre (`garantie_foyer`,
`frais_reserve`, `allocation`, `derive_revalorisation`), `parametre`
additionne et `recette` ventile son retrait par payeur.

*« Divise la dérive par dix »* était écrit en cinq endroits, sans que
personne dise de quelle dérive. En médiane sur les années de perception, la
colonne de 2019 reconstruite depuis 2026 s'écarte de 0,135 %, depuis la
suivante de 0,007 % ; au pire, toutes colonnes confondues, de 0,26 % contre
0,12 %, un facteur deux, et c'est ce pire que le test tient. Le tableau de
`limites.md` datait d'avant la colonne de 2025 et était gelé comme un
procès-verbal : il se recalcule, et les docstrings ne recopient plus de
chiffre.

*Les deux dettes du README* ne demandaient qu'une sonde qui sache lancer
`node`. `portage` fait le compte de `tests/js/comparer.mjs` sur les témoins,
dans un processus à part : 73 846 nombres comparés et non 10 615, dont
88,1 % identiques au bit près et non 97,9, l'écart maximal à 7,8 · 10⁻¹⁵.

*Les trois sections de l'outillage* restaient non déclarées parce que leurs
tailles décrivent des logiciels installés hors du dépôt. Mais elles décrivent
une VERSION, et une version publiée ne change plus :
`test_les_chiffres_de_l_outillage_sont_ceux_des_versions_figees` lie chacune
à la sienne et échoue dès que le dépôt en fige une autre. Remesurées le même
jour : 16 089 424 octets pour le moteur 0.1.5, 5 constats et 8 000 caractères
par défaut pour son hook, 196 289 395 octets pour l'archive de Chrome for
Testing 154.0.8037.0 qu'attend le CLI 0.1.20.

**Ce que la passe a appris.** Une autre session corrigeait au même moment les
lois de mortalité projetées, restées calées sur d'anciennes cibles ; moins
d'une heure après leur ancrage, trois chiffres de la méthodologie avaient
bougé, et `--corriger` les a réécrits sans qu'on les cherche. C'est l'argument de
l'action. Le même « 8 % de rente » était écrit en dur dans un commentaire de
`config.py` et dans deux notes du fichier des frais, dont l'une disait encore
que le modèle ne retient pas le frais sur la réserve : la prose non déclarée
vieillit aussi, et c'est une mesure devenue disponible qui l'a montré.

**Ce qui reste, et ce n'est plus une dette.** Les angles morts que
`docs/fraicheur.md` nomme : les petits nombres en toutes lettres, les blocs
de code — le compte des tests de l'arborescence du README est tenu par son
propre test —, et les phrases, qui sont l'objet de l'action 34. Une
découverte, laissée à une session qui tient les pages : le tableau d'accueil
du site, « Ce que le plancher individualisé change », intitule « Aujourd'hui
(ASPA) » une colonne qui applique au foyer les planchers de la garantie —
1 000 € pour un couple à 300 et 300 €, 750 € pour une personne seule à
300 € —, quand l'ASPA de 2026 en servirait environ 1 020 et 743,59. Le
libellé est un choix du programme, et il se fait dans les deux moteurs.

**Fichiers.** `scripts/verifier_prose.py`, `data/reference/prose/zones.yaml`,
`tests/test_prose.py`, `docs/fraicheur.md` (neufs) ; les ancres posées dans
`README.md`, `docs/feuille_de_route.md`, `docs/limites.md`,
`docs/methodologie.md`, `docs/avantages_non_contributifs.md`,
`docs/veille_droit.md` et `docs/integration-partiliberalfrancais.md`.

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

**La lecture d'un graphique ne fait plus sauter la page.** Signalé après
la seconde passe : en balayant vite un tracé à la souris, « la légende
saute ». Deux causes, toutes deux dans la bande de lecture que la seconde
passe avait mise à la place de la légende : ses entrées se repliaient
autrement à chaque année selon la largeur des chiffres, et la légende qui
disparaissait puis revenait à chaque entrée et sortie du pointeur changeait
la hauteur de la figure. La bande n'est plus affichée — elle reste la
région vocale, qui dit maintenant une phrase par année — et les valeurs
s'écrivent DANS la légende, dans une case par série, vide au repos, que le
script dimensionne au rendu à la plus longue valeur de la série (autant de
`ch` que de caractères, les chiffres étant à chasse fixe). L'année s'écrit
en haut du trait de repère, dans le tracé, avec le halo des étiquettes de
série. Mesuré en balayant quarante positions sur Coût et Trajectoire, à
360 et 1 280 points : la figure garde une seule hauteur, et les entrées de
la légende une seule position, du repos à la sortie du pointeur.

**Rien ne sort des graphiques, et ils se lisent partout.** Demandé après
la lecture au survol. Vérification systématique : chaque graphique de huit
routes (deux simulations, deux trajectoires, Coût, Avantages, Méthode,
l'accueil), dépliants ouverts, à 320, 360, 768, 1 280 et 1 920 points ; pour
chaque texte du tracé, sortie du cadre, chevauchement avec un autre texte,
taille rendue sous 10 pixels ; pour chaque tracé, sortie du cadre ; pour la
légende, débordement de la figure ; puis le survol de CHAQUE année, une par
une, en faisant défiler la figure quand le tracé est plus large que
l'écran : l'année écrite en haut du trait ne doit ni sortir ni recouvrir un
autre texte, les points ne doivent pas sortir, et la case de chaque valeur
dans la légende doit la contenir. Quatre défauts trouvés, corrigés le jour
même. *Le clignotement* : l'écoute de `pointerleave` en capture recevait
la sortie de CHAQUE élément — une courbe, un cercle, le trait que le survol
venait de redessiner sous le doigt — et effaçait la lecture à chaque fois ;
seule la sortie de la figure compte désormais. *L'année sur l'unité* :
pour les premières années, l'étiquette de l'année recouvrait l'unité de
l'axe, dans le même coin ; elle s'écarte maintenant du trait de la largeur
de l'unité. *Le zéro sur la première année* : sur téléphone, le « 0 » de
l'axe vertical et la première graduation d'année se touchaient ; les années
descendent de trois unités. *La case trop juste* : dimensionnée en `ch`,
elle débordait d'un pixel — les chiffres tabulaires en graisse 800 sont plus
larges que le zéro qui définit le `ch` ; elle est maintenant mesurée dans
la case elle-même sur les valeurs les plus longues, et ne rétrécit jamais.
Après correction, la vérification ne rend plus rien : zéro constat sur
1 720 survols et 48 graphiques. Le script est `graphiques.mjs`, à
reprendre pour une passe suivante — il faudrait qu'il rejoigne `scripts/`.
Une chose apprise : la suite de tests ne charge pas `index.html` dans un
navigateur, et une déclaration en double dans son script a rendu le site
blanc sans qu'aucun test ne le dise ; c'est la vérification elle-même qui
l'a vu. Un test qui analyse ce script avec `node --check` coûterait dix
lignes.

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

**Le bilan vie entière, le même jour** (`--vie-entiere`). La page Coût retire
aux scénarios notionnels les 10,9 milliards que la branche famille verse à la
retraite en 2024 — AVPF et majorations pour enfants — et dit que l'argent lui
reste ; le programme le rend aux familles à la naissance. Le second tableau en
tire la conséquence : 10,9 milliards pour 663 000 naissances font 16 386 € par
enfant, suivis du salaire moyen jusqu'à l'année où chaque enfant naît, et le
bilan compare la pension du scénario 1 servie sur l'espérance de vie à la
liquidation à celle du scénario 6 sur la même durée, plus l'aide reçue. Le
chiffre des naissances est celui du bilan démographique de l'INSEE, et il
n'est pas dans les données du dépôt : c'est la seule hypothèse du tableau qui
ne soit pas lue. **Une mère de plusieurs enfants n'y gagne pas.** Portée au
compte à chaque naissance et revalorisée comme lui, l'aide vaut à la
liquidation 74 € par mois pour un enfant, 146 € pour deux, 216 € pour trois,
quand le scénario 1 sert 134, 143 et 366 € à carrière complète, 543 et 846 €
avec trois et six ans d'arrêt. À deux enfants sans arrêt, l'aide égale le
droit ; partout ailleurs elle est en dessous, et de loin dès que la mère
s'est arrêtée, parce que l'AVPF est concentrée sur celle qui s'arrête quand
l'aide est répartie sur toutes les naissances. Sur la vie entière, en euros de
2026 et sans actualisation, le solde va de −200 000 € sans enfant à −296 000 €
pour trois enfants et six ans d'arrêt : l'essentiel de l'écart n'est pas
l'enfant, c'est le compte lui-même, qui sert 30 % de moins à la salariée du
privé sans enfant. Ce que le bilan ne compte pas : les cotisations de la mère,
identiques par construction (18 + 5 + 5 contre 28) ; la réversion ; les
allocations familiales et la PAJE, qui existent sous les deux systèmes.

---

### 44. La décomposition des avantages sur la page Coût — `fait`

**Pourquoi.** L'action 37 a chiffré les avantages non contributifs à 22,3 % de
la dépense, et leur a donné une page. La page Coût, elle, décompose la dépense
par régime et par recette, sans jamais dire quelle part n'a été cotisée par
personne. Les deux pages parlent du même argent et ne se parlent pas.

L'objection qui retenait ce portage est levée par l'action 37 : tant que la
décomposition mesurait 1,2 % de ce qu'elle prétendait mesurer, l'afficher
ailleurs aurait trompé.

**La décision à prendre, et elle n'est pas technique.** Reprendre la
décomposition sur la page Coût, ou n'y poser qu'un renvoi. Reprendre coûte un
graphique de plus sur une page qui en porte déjà beaucoup, et fait cohabiter
deux périmètres — la dépense du compte du système de retraite et celle du risque
vieillesse-survie des comptes de la protection sociale — qui ne sont pas le
même nombre. Renvoyer coûte un clic, et laisse la page Coût dire « voilà ce que
ça coûte » sans dire « et voilà ce que personne n'a payé ».

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `moteur/js/pages.js`
en regard ; les témoins. Rien dans le modèle : `avantages.py` rend déjà tout ce
qu'il faut, et `calculer_avantages` est appelable depuis la page Coût sans un
calcul de plus.

**Le piège à nommer d'avance.** Les deux pages n'ont pas le même dénominateur.
Poser 22,3 % sous une courbe qui rapporte au PIB, ou à côté d'une dépense qui
n'est pas celle du même compte, ferait un chiffre faux sans qu'une ligne de code
soit fautive.

**Fin.** Un lecteur de la page Coût sait quelle part de la dépense n'a été
cotisée par personne, ou sait où aller le lire.

**Ce qui est fait, le 20 septembre 2026.** Les deux à la fois, chacun à sa
place, et le piège tranche la question du dénominateur. La page Coût porte
deux comptes : les cartes du haut suivent le COR, à la dernière année qu'il
observe ; le dépliant « Le détail des dépenses » suit la DREES, risque
vieillesse-survie entier, à la dernière année qu'elle publie — et c'est ce
total-là, à cette année-là, que `calculer_avantages` prend pour `observee`.
La part n'a donc qu'une place où elle soit juste : ce dépliant. Il gagne une
section « Ce que personne n'a cotisé », un tableau par famille de
l'inventaire, le même découpage que la page Avantages, avec le montant et la
part de la dépense, et une ligne d'ensemble ; le paragraphe qui l'introduit
nomme le total sur lequel la part se lit et dit qu'il n'est pas celui des
cartes. En haut de page, entre la carte « Qui paie ? » et la note « Dépenser
moins n'est pas économiser », une note de quarante mots donne le total, le
montant, la part, et renvoie à la page Avantages — elle porte son propre
dénominateur et son année, précisément pour ne pas se lire sous les trois
chiffres d'ouverture. Pas de graphique : la page en a deux et n'en aura pas
trois, et le dispositif par dispositif reste sur la page qui sait dire
pourquoi une case est vide.

**Ce que ça a déplacé.** Rien dans le modèle, rien dans `simulations.json` :
`calculer_avantages` était déjà appelé par le dépliant de la garantie, la
page ne calcule pas une seconde de plus. Sur la page, en 2024 : 96,2 Md€
sur 426,7, soit 22,5 % — 46,0 de droits dérivés, 22,7 d'âge et de
bonifications, 11,2 de droits familiaux, 7,8 de minima, 7,3 de périodes
validées, 1,2 de majorations diverses. La page ouverte passe de 650 à 688
mots, sur un budget de 700 : la prochaine phrase ajoutée en haut de Coût devra
en déloger une autre. La page avait deux bornes, 650 dans son propre test et
700 dans `BUDGETS_DE_LECTURE`, et se trouvait à 650 exactement ; le test de
la page lit désormais le budget, une borne au lieu de deux.

**Fichiers.** `web/pages.py` (`_cout`, `_cout_detail_depense`) et
`moteur/js/pages.js` en regard ; `tests/test_web.py` ;
`tests/temoins/pages.json`.

### 45. Les sources qui refusent la session se déclarent, et leur document s'apporte — `fait`

**Demande.** « Est-ce qu'on a une liste de tous les liens bloquants ? On
pourrait utiliser Playwright sur mon ordinateur personnel pour aller chercher
les fichiers manquants ? » Puis : « ajoute le champ dans sources.yaml et
l'option fichier local ».

**Le diagnostic.** Il n'y avait pas de liste. Ce qu'une session ne peut pas
atteindre était écrit trois fois et rassemblé nulle part : dans la note du jeu
de `data/sources.yaml` quand quelqu'un avait pensé à l'y mettre, dans
`docs/limites.md` pour les entrées fermées, dans `docs/outillage_interface.md`
pour la règle. Le manifeste avait un champ pour le format (`acces`) et un pour
l'avancement (`statut_integration`), aucun pour « joignable ou non ». Et le
jaune pensions, apporté par l'utilisateur en septembre 2026, avait été lu à
l'écran et saisi : aucun récupérateur ne savait lire un fichier déposé, et
`data/brut/` — le lieu que le manifeste désignait pour cela — n'était visité
par personne.

**Ce qui est fait.**

- **Le champ `blocage`** dans `data/sources.yaml`, documenté dans l'en-tête :
  `refus` (le site repousse la session, un navigateur ordinaire passe),
  `reseau` (la machine ne joint pas le site), `convention` (clé, compte ou
  convention). Sept jeux le portent : le jaune pensions et les deux projets
  annuels de performances de `budget.gouv.fr` — lus le même jour par une
  autre session, apportés par l'utilisateur —, le rapport de l'OPEF à
  la Banque de France, les deux entrées Légifrance, et l'EIC de la DREES
  sous convention. `fichier_local` déclare le nom attendu quand l'adresse n'en porte
  pas.
- **`scripts/fetch/source_locale.py`**, la liste et le mécanisme. Lancé sans
  argument, il imprime les jeux bloqués, la nature du blocage et, pour chacun,
  le chemin où son fichier est attendu. Importé, il donne
  `lire_ou_telecharger`, qui lit `--fichier` s'il est passé, sinon
  `data/brut/<nom du fichier>` s'il existe, et ne télécharge qu'en dernier ;
  et `option_fichier`, l'option elle-même.
- **Six récupérateurs y passent** : Agirc-Arrco, ERAFP et projections de
  mortalité INSEE avec `--fichier` (un document chacun) ; circulaires Cnav,
  barèmes CNBF et recueils CNAVPL par `data/brut/` (plusieurs documents, un
  nom chacun ; les recueils, que le site sert sous `?wpdmdl=…`, sont attendus
  sous `cnavpl_recueil_<année>.pdf`).
- **`tests/test_source_locale.py`** : une valeur de `blocage` inconnue du
  module est refusée, un blocage sans note aussi, `fichier_local` sans blocage
  aussi ; l'ordre fichier, dépôt, site est vérifié sans réseau ; les six
  récupérateurs appellent bien le module.

**Ce qui n'est pas fait, et pourquoi.** Aucun récupérateur ne lit encore le
jaune pensions ni le rapport de l'OPEF : leurs valeurs sont saisies, et
écrire le lecteur demande le document sous la main. C'est le pas suivant, et
il commence sur le poste de l'utilisateur : télécharger le jaune, le déposer
dans `data/brut/`, et le manifeste dira sous quel nom dès que `fichier_local`
sera renseigné. `data/brut/` reste hors de git — un PDF de plusieurs mégaoctets
n'a pas sa place dans l'historique — et c'est le lecteur, versionné, qui
rendra la valeur recontrôlable.

**Le même jour, la suite : le miroir.** « Je voudrais que tu puisses faire en
automatique la récupération de tous les fichiers dont tu as besoin avec le
moins d'interventions de ma part possible. » La pièce jointe ne passait pas,
la release GitHub demandait un geste. Or les annexes budgétaires sont
déposées au Parlement, et l'Assemblée nationale sert le même PDF, octet pour
octet, à une session : le jaune pensions 2026 (349 pages, 5,7 Mo), le PAP du
CAS Pensions et celui de la mission « Régimes sociaux et de retraite » se
sont téléchargés d'ici. D'où deux champs de plus sur un jeu bloqué, `miroir`
et `sha256`, une commande, `source_locale.py --recuperer`, qui dépose chaque
miroir dans `data/brut/` et refuse un fichier dont l'empreinte diffère, et
`lire_ou_telecharger` qui essaie le miroir avant l'adresse refusée. Quatre
tests de plus. Le rapport de l'OPEF reste le seul sans miroir : vie-publique
porte l'édition 2025, pas encore la 2026.

**Ce qui s'ouvre.** Le jaune est là, mais sa police n'a pas de table
Unicode : `lecture_pdf.py` en rend le titre comme « 5DSSRUW » — chaque lettre
décalée de 29. Le lecteur qui certifiera les tableaux A-7, 50 et B-1 devra
d'abord lever ce décalage, ou passer par un extracteur qui lit les tables
de police. C'est le pas suivant, et il ne demande plus rien à personne.

**Fin.** Une commande dit ce que le dépôt ne peut pas aller chercher, une
autre va le chercher là où on le sert quand même, et un fichier déposé au
bon endroit est lu sans qu'on touche au script.

**Le même jour, encore : le dépôt se fait son propre miroir.** Le rapport de
l'OPEF n'a pas de miroir public (vie-publique porte l'édition 2025, le CCSF
renvoie à la Banque de France). D'où `source_locale.py --publier` et le
workflow `documents-apportes.yml` (à la main, et le 3 de chaque mois) : sur
un runner GitHub, chaque jeu `refus` sans miroir est téléchargé depuis son
adresse de document — nouveau champ `document` du manifeste quand `url` est
une page —, par une requête simple puis, si le site refuse, par un Chromium
Playwright headless ordinaire installé à ce moment-là seulement, sans rien
maquiller ; le fichier est déposé sur la release `documents-apportes`, avec
son empreinte et sa date dans le corps, et l'asset devient le `miroir` du
jeu. `--recuperer` cherche déjà la release quand aucun miroir n'est déclaré.
Vérifié de bout en bout ce jour : le workflow, déclenché trois fois par
l'API, fait ses deux passes et a créé la release ; les trois annexes
budgétaires se rapportent depuis la session ; un asset de release se
télécharge par le même chemin. Ce qui ne passe pas : la Banque de France
refuse le runner comme la session, 403 Akamai « Access Denied », page et
PDF, requête simple et navigateur — une décision sur l'adresse du client,
que le dépôt ne contourne pas. L'unique geste qui reste, une fois : déposer
`OPEF2026.pdf` sur la release `documents-apportes` (onglet Releases) ; le
workflow le conserve ensuite, et `--recuperer` imprime l'empreinte à
inscrire dans le manifeste. Onze tests de plus, sans réseau.
- **20 septembre 2026, action 46.** Faite. L'emploi projeté suit le scénario
  de référence du COR de juin 2026 pour les systèmes 2 à 6, par la masse
  salariale ; le système 1 ne le lit pas. Le détail est sous l'action. À
  retenir : la trajectoire du COR n'est pas un choc favorable — +3,7 % pour
  la génération 1975, −5,2 % pour la génération 2000 —, et le PIB de la page
  Coût ne la lit pas encore.
- **20 septembre 2026, action 48.** Faite. Les pensions déjà servies à la
  bascule gardent les prix, et la bosse de la page Coût disparaît sans que
  l'horizon bouge. Ce qui reste du déficit de la proposition en 2039, 1,27
  point de PIB, est le coût de transition du 18 %, et c'est l'action 11 qui
  l'attend.
- **20 septembre 2026, relecture.** Le § 4 du README portait les tableaux de
  la page Coût d'avant les actions 46 et 48, et déjà d'avant les actions
  précédentes : personne ne les recompte, à la différence du bloc d'exemple
  du § 3. Ils sont remis aux chiffres du jour et datés. Et le tableau « par
  horizon » de la page Coût titrait ses colonnes « Notionnel dès 2026 » quand
  il montre, depuis l'action 31, le compte notionnel à deux parts et la
  proposition : les en-têtes disent désormais ce que les colonnes portent, sur
  les deux moteurs.
- **20 septembre 2026, action 34, un cas refermé.** Cas types promettait en
  texte fixe un coefficient d'équilibre « supérieur à un chaque année » pour
  la proposition, quand Coût le chiffrait sous un sur toute la projection.
  La phrase est calculée depuis le solde sur les deux moteurs, la note de
  Coût lit le coefficient dans les deux sens, deux tests tiennent les pages
  et le tableau du README, le parcours de présentation ne promet plus de
  marge. Le détail est sous l'action, qui reste à faire pour le catalogue.
- **20 septembre 2026, le parcours de présentation est tenu par un test.**
  Le document qu'on suit pour parler en public portait les chiffres d'une
  matinée, gelés dans une zone `recit` que rien ne relit. Le modèle a bougé
  quatre fois dans la journée, et le parcours demandait d'annoncer une baisse
  du salaire net là où l'écran montrait une hausse de trois cents euros ;
  cinq autres chiffres avaient dérivé, dont trois comptes sans unité que
  l'œil ne signale pas. `tests/test_parcours.py` rejoue les adresses que le
  document donne, rend ses pages, et refuse tout montant, tout pourcentage et
  tout compte que le site n'affiche pas ; ce qui vient d'ailleurs se déclare
  dans `HORS_PAGE` avec sa raison, et un test tient cette liste courte. Le
  parcours gagne au passage la page Risque, la ligne « financé » du système 1
  et les deux comptes de la page Avantages, 37 en vigueur sur 43 recensés,
  qui se croisent sans que la page les distingue.

### 46. L'emploi projeté suit le scénario de référence du COR, pour les systèmes 2 à 6 — `fait`

**Ce que c'est.** Jusqu'au 20 septembre 2026, l'emploi salarié était supposé
constant au-delà de 2025 : la masse salariale projetée — le rendement des
comptes notionnels — était le seul salaire moyen. L'action remplace cette
convention par la trajectoire d'emploi du scénario de référence du rapport
annuel du COR de juin 2026, dérivée de sa population active et de son taux de
chômage (`data/reference/macro/emploi_projete.csv`, source
`cor_projection_emploi`), et composée année par année avec le salaire moyen
du scénario de productivité. La trajectoire ne touche que la masse salariale
et le PIB projetés, que seule l'indexation des comptes lit : le système 1 ne
bouge pas, les systèmes 2 à 6 la reçoivent. C'est ce qui a été demandé — un
emploi qui bouge sous la réforme, pas sous le droit constant — et c'est
écrit sur le formulaire (« Emploi projeté », systèmes 2 à 6 seulement) et
dans le bloc « Ce que l'hypothèse pèse » de la page de résultats, qui rejoue
le système 2 sous l'autre trajectoire.

**Ce que ça a déplacé.** Mesuré le 20 septembre 2026 sur un salarié non cadre
entré à 22 ans et parti à 64 ou 65 ans, systèmes 2 à 6 contre l'emploi
constant : +3,7 % pour la génération 1975, −1,0 % pour 1990, −5,2 % pour 2000.
Le COR fait monter l'emploi de 4,7 % jusqu'en 2040 puis reculer de 6,0 % en
2070 : la trajectoire est favorable à qui liquide dans la bosse, défavorable
ensuite. Elle n'est pas le choc d'offre du programme, elle est la projection
à législation constante du COR ; le choc, s'il doit être chiffré, sera une
trajectoire de plus dans `trajectoires_emploi`, avec sa source, et il faut
savoir que le point de départ est déjà en dessous de la ligne d'emploi
constant après 2050.

**Ce qui reste.** Le PIB de la page Coût garde la population des 20-64 ans
comme correction (`limites.md` § 5 ter) et ne lit pas la trajectoire ; y
substituer l'emploi du COR, pour les systèmes réformés, est la marche
suivante — elle touche `cout.py` et `cout.js`, où le PIB est unique par
année. Une variante de productivité à 1,3 %, demandée pour le système 2, n'a
pas été retenue : le COR l'a abandonnée en juin 2025 pour ralentissement
structurel, et un choc d'emploi n'est pas un supplément de productivité.

**Fichiers.** `data/reference/macro/emploi_projete.csv`,
`hypotheses_projection.yaml` (`trajectoires_emploi`), `donnees/macro.py`,
`moteur/js/macro.js`, `config.py`, `config.js`, `web/pages.py`,
`moteur/js/pages.js` (champ `emploi`), `construire_donnees.py`,
`construire_temoins.py` (cas `emploi_constant`), `tests/test_donnees.py`,
`tests/test_simulateur.py`, `limites.md` § 1 et § 5 ter, `sources.yaml`.

---

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

### 48. Les pensions déjà servies à la bascule gardent les prix — `fait`

**Ce que c'est.** Sur la page Coût, une réforme prospective faisait passer
tout le stock des pensions en cours à la règle du compte le jour de la
bascule. C'était offrir aux retraités de 2026 un demi-point par an pendant
quinze ans, que personne n'avait cotisé, et c'était la bosse de dépense de
2026 à 2040 que l'action 46 avait fait monter à 7,5 % au-dessus du système
actuel. Le défaut est désormais celui du droit : une pension liquidée sous le
système actuel garde l'indice des prix jusqu'à son extinction, et seuls les
comptes ouverts sous le nouveau régime suivent sa règle. La réindexation reste
en variante, réglage « Pensions en cours à la bascule » du formulaire, et un
témoin la mesure.

**Ce que ça a déplacé.** Mesuré le 20 septembre 2026, trajectoire du COR : le
système 3 ne dépasse plus jamais le système actuel (sommet 0,998 en 2026, au
lieu de 1,049 en 2034), le système 5 culmine à 1,011 en 2039 au lieu de 1,075,
la proposition passe de 0,822 à 0,775 en 2039. Le solde de 2039 gagne 0,8 point
de PIB pour le système 3, 0,8 pour le 5 et 0,6 pour la proposition, dont le
déficit reste à 1,27 point : ce qui reste est le coût de transition du 18 %,
qu'aucune règle d'indexation ne règle. En 2070, rien ne bouge au millième.

**Ce qui reste.** Le coût de transition, précisément : le coefficient
d'équilibre de l'action 11, ou une recette de transition explicite. Et deux
populations de retraités sous deux règles pendant trente ans, ce que la page
dit.

**Fichiers.** `config.py` (`RevalorisationStock`), `cout.py`
(`coefficient_stock`), `moteur/js/cout.js`, `web/pages.py` et
`moteur/js/pages.js` (champ `stock`, encart de la page Coût),
`construire_temoins.py` (`REGLES_AUTRES`), `tests/test_cout.py`,
`limites.md` § « Et le stock, le jour de la bascule ».

### 49. Le jaune pensions, lu par le dépôt : le lecteur PDF réparé, trois tableaux, trente-neuf chiffres retrouvés — `fait`

**Demande.** « Débrouille-toi pour analyser le PDF du jaune. » Le document
était là depuis l'action 45, par son miroir à l'Assemblée nationale ; le
lecteur PDF du dépôt en rendait « 5DSSRUW » pour « Rapport ».

**Le diagnostic, en quatre défauts du lecteur.** `lecture_pdf.py` ne dépliait
pas les flux d'objets compressés (`/ObjStm`), où un PDF 1.5 range ses pages
et ses polices : il ne voyait aucune police, donc aucune table. Il n'appliquait
pas la table ToUnicode aux chaînes littérales, seulement à l'hexadécimal — or
une police TrueType sous-ensemble numérote ses glyphes dans l'ordre
d'apparition et les pose en `(\001\002…)`, un octet par code. Il tenait une
table unique par nom de police pour tout le document, quand Word donne à
chaque page son `/TT0` et sa table. Et le rang du groupe qui devait porter le
nom de la police, écrit en dur, désignait en fait le groupe de la chaîne : le
nom restait à `None`, et aucune table n'avait jamais été appliquée aux
chaînes — depuis l'origine. Puis trois défauts de lecture qui salissaient les
tableaux : les espaces posées seules (`( ) Tj`) étaient jetées, ce qui collait
les mots ; les dictionnaires du contenu balisé (`<</Lang (en-US)>>`)
s'imprimaient entre chaque cellule ; et la fine insécable des milliers
devenait une espace ordinaire, si bien que « 1 339 945 1 654 863 » ne se
découpait plus en deux nombres.

**Ce qui est fait.**

- **`scripts/fetch/lecture_pdf.py`** apprend les sept points : flux d'objets,
  chaînes littérales traduites par la table avec la largeur de code que son
  `codespacerange` déclare, polices résolues page par page et formulaire par
  formulaire (`/Resources` puis `/Font`, rattachés au flux `/Contents` ou au
  `/Form`), nom de police pris par le groupe nommé, espaces seules gardées,
  dictionnaires sautés, insécables gardées insécables, reculs d'un tableau
  `TJ` rendus en espace, images JPEG ignorées. Toujours sans dépendance. Le
  jaune se lit en sept secondes. `tests/test_lecture_pdf.py` : huit documents
  minimaux fabriqués à la main, un par point.
- **`scripts/fetch/sre_jaune_pensions.py`** lit le document — `data/brut/`,
  sinon le miroir, avec l'empreinte du manifeste — et en tire les trois
  tableaux qui servent au dépôt : A-7 (six bonifications × cinq colonnes, sur
  le stock 2024), 50 (trois blocs × quatre populations × huit colonnes, sur le
  flux 2023), et les lignes complètes de B-1. Deux contrôles refusent
  d'écrire : plus de bénéficiaires que de pensions, un ensemble sous une
  bonification seule. Sortie : `data/brut/sre_jaune_pensions.json`.
- **`--confronter`** relit `avantages_non_contributifs.yaml`, extrait les
  nombres de chaque note qui cite le jaune, et dit s'ils sont dans les
  tableaux lus : **trente-neuf sur trente-neuf** le 20 septembre 2026. La
  saisie faite à l'écran est prouvée par le document. Neuf tests dans
  `tests/test_sre_jaune_pensions.py`, sur les lignes que le lecteur rend.

**Ce qui reste, et pourquoi.** Le jeu reste `saisi` : la confrontation prouve
la saisie, elle ne la remplace pas par une valeur lue, faute d'un champ
structuré dans le fichier cible — les chiffres y vivent dans des notes. Le
passage à `certifiee` demande ce champ et sa lecture par
`verifier_donnees.py`, c'est-à-dire une décision sur la forme du fichier des
avantages, pas une lecture de plus. Et un défaut du document lui-même : la
table Unicode d'une de ses polices n'a pas les lettres accentuées, si bien que
« bénéficiaires » s'y lit « bnficiaires » — pdfminer rend la même chose ; les
intitulés sont reconnus sans accents, les nombres sont intacts.

**Fin.** Le jaune se lit, ses trois tableaux sont dans un JSON, et chaque
chiffre qu'on en avait recopié est retrouvé dans le document par un script.

**Le même jour, la suite : le champ structuré, et les valeurs certifiées.**
« Ajoute le champ structuré pour certifier les valeurs du jaune. » Les
chiffres vivaient dans des notes ; le vérificateur ne sait certifier qu'un
CSV à clés, colonne `fiabilite`, et réécrire un YAML avec ses commentaires
n'est pas à sa portée. D'où la forme : les trois tableaux, à plat, dans
`data/reference/legislation/bonifications_jaune.csv` — clé (tableau, ligne,
population, mesure), 143 valeurs, toutes `certifiee` —, écrit par
`verifier_donnees.py --appliquer` depuis le JSON du lecteur, par deux
certifications sur le même fichier, l'une pour les entiers (effectifs,
euros), l'autre pour les décimaux (durées, proportions), parce qu'un format
unique aurait écrit « 404478.000 » ou « 27 ». Et sur chacune des cinq fiches
qui citent le jaune, un champ `denombrement` : `source_id`, la ligne du
tableau A-7 (le stock, où le document confond campagne et cinquième) et la
colonne du tableau 50 (le flux, où il les sépare). `tests/test_bonifications_jaune.py`
tient l'ensemble : le CSV ne porte que du certifié, le champ désigne des
lignes qui existent, et chaque chiffre qu'une note cite du jaune est une
valeur certifiée de ses lignes — la prose ne peut plus s'écarter du document.
Le jeu `sre_jaune_pensions` passe à `certifie` dans le manifeste, et le
journal de certification porte ses deux traces.

### 50. Les frais du pilier capitalisé, questionnés sur le document du producteur — `fait`

**Demande.** « Je souhaiterais qu'on questionne les frais de la capitalisation,
cela influe beaucoup, il ne faut pas se tromper. »

**Ce qui a été trouvé.** Les trois valeurs (1,09 % sur versement, 0,76 % par
an sur encours, 2,20 % sur arrérages) avaient été saisies depuis la presse, le
serveur de la Banque de France refusant le rapport de l'OPEF à la session comme
au runner. Le rapport a été obtenu par l'outil de lecture web de Claude Code,
qui sort par un autre chemin, et il confirme la saisie : tableau T7, exercices
2024 et 2025, six valeurs identiques. Il dit aussi ce que la presse n'avait
pas repris. La moyenne des frais sur arrérages est **non pondérée et ne porte
que sur les neuf assureurs, sur vingt, qui les facturent** : onze ne prélèvent
rien sur la rente. Le frais sur versement du PER est le double de celui de
l'assurance-vie (0,55 %) et six fois celui du contrat de capitalisation
(0,19 %), pour les mêmes fonds en euros : l'OPEF y voit des frais fixes sur des
primes petites, ce qu'une cotisation sur chaque paie n'a pas. Et le frais de
gestion du fonds en euros est proche partout (0,67 à 0,76 %) : c'est le prix
d'un fonds en euros d'assureur, garantie comprise, pas celui d'une échelle de
titres d'État.

**Ce que coûte un régime obligatoire, pour situer la borne haute.** La prime
de pension suédoise, seul pilier capitalisé obligatoire adossé à un compte
notionnel, coûte 0,11 % des encours en frais de fonds après remise et 0,024 %
d'administration ; le FRR, 0,41 % toutes charges comprises en gérant des
actions, dont 8,6 points de base de coûts fixes ; l'ERAFP provisionne « au
moins 0,2 % ». Aucun ne prélève sur les versements ni sur les arrérages. Trois
jeux `controle` dans le manifeste les portent.

**La taille du biais, mesurée.** Sur une carrière entière après la bascule, la
rente du pilier serait supérieure de 1 % sans frais sur versement, de 13 % avec
une gestion à 0,20 %, de 18 % au barème d'un fonds public, de 22 % sans aucun
frais ; le repère « environ 10 % » de `limites.md` pour la gestion à 0,20 %
était sous-estimé. Le frais de gestion est le poste qui compte, parce qu'il
s'applique chaque année à tout l'encours. Le tableau est dans `limites.md`
§5 ante, point 3.

**Ce qui a été fait.** `scripts/fetch/opef_frais_per.py` lit les tableaux T5 à
T7 du rapport avec pypdf (le lecteur du dépôt ne rend pas ses polices CFF), et
`--confronter` compare le T7 au fichier de référence ; sept tests sur le texte
rendu. Le fichier de frais, le manifeste (empreinte du document, confrontation,
trois sources de contrôle), la page Méthode, la page du pilier, `limites.md` et
`methodologie.md` disent ce que le document ajoute.

**Ce qui n'a pas été changé, et pourquoi.** Le barème par défaut. Le remplacer
par un barème de pilier obligatoire est une décision de proposition, pas une
lecture : la borne haute reste le réglage, et les trois paramètres se changent
en un endroit. Le niveau reste `haute` : `certifiee` demanderait que
`verifier_donnees.py` lise ce fichier, qui n'est pas une série. Le document
reste à déposer une fois, à la main, sur la release `documents-apportes`, avec
l'empreinte inscrite au manifeste.

**Le même jour, la suite : les vraies moyennes et les médianes.** « Je veux
que l'on ait les chiffres des vraies moyennes et des vraies médianes ; pas
seulement ceux qui font payer. » Ce que l'OPEF pondère et ce qu'il ne pondère
pas a été relu : versement et gestion sont des moyennes pondérées de tout le
marché, par les primes et par l'encours moyen, donc les vraies moyennes de ce
qui est payé ; les arrérages, une moyenne non pondérée des seuls facturants,
d'où 0,99 % sur les vingt déclarants et une médiane nulle, que le récupérateur
déduit désormais. Aucune médiane n'est publiée pour les deux premiers, ni par
l'OPEF ni par le CCSF, dont le rapport de 2021 sur 34 PER assurance a été
obtenu et lu : versement maximum affiché 3,18 % (0 à 5), gestion 0,87 % (0,60
à 1 hors un fonds à 2), arrérages 1,18 % zéros compris, onze contrats sur
trente à zéro. Et une trouvaille : 22 contrats sur 34 prélèvent aussi 0,60 à
1 % par an sur l'encours de rentes, un frais que l'OPEF ne mesure pas et que
le modèle ne compte pas, qui vaut 9 à 15 % de rente au diviseur du modèle,
quatre à sept fois l'effet des arrérages. Le fichier de frais porte un bloc
`distributions` avec tout cela, le manifeste un jeu `controle` pour le CCSF,
et `limites.md` §5 ante le tableau. Le barème du calcul reste inchangé.

### 51. Les deux PAP, lus par le dépôt : 242 valeurs au niveau haute — `fait`

**Demande.** « Fais pareil pour les deux PAP » — après le jaune —, et
« j'ai rajouté l'OPEF dans le dépôt directement ».

**Les PAP.** `data/reference/regimes/pap_regimes_subventionnes.csv` portait
294 valeurs saisies à la lecture des deux projets annuels de performances
du PLF 2026, apportés par l'utilisateur : la mission « Régimes sociaux et de
retraite » et le CAS Pensions, que l'Assemblée nationale sert depuis
l'action 45. `scripts/fetch/pap_plf_2026.py` les relit en trois familles :
les séries 2012-2023 du programme 198 par leur ligne d'années — le libellé
sur trois lignes, les douze valeurs au milieu, les milliers séparés
d'espaces ordinaires que seul le compte des colonnes découpe —, les crédits
2026 par la ligne « Hors titre 2 » de chaque action, et les points en prose
par des motifs cherchés dans le texte SANS AUCUNE ESPACE, parce que le PDF
en glisse au milieu des mots (« direc t », « prévisi on ») et que le CAS
écrit ses apostrophes et son signe euro en codes Windows-1252 que sa police
ne traduit pas. Résultat : 242 valeurs lues sur 294, 242 identiques à la
saisie, zéro écart. `verifier_donnees.py` les recontrôle et les verse au
niveau `haute` — pas `certifiee` : le producteur est la caisse, le PAP la
transcrit, et une transcription tierce plafonne là même lue par un script.
Les 52 autres restent `moyenne` : les 48 âges moyens de départ, écrits
« 55 ans et 8 mois » sur trois lignes enchevêtrées, la subvention 2023 de la
Comédie-Française, les engagements de la SEITA et les crédits 2025 des
marins, que le texte ne porte pas tels quels. Le vérificateur accepte
désormais `decimales=None` — chaque valeur au plus court — pour un fichier
dont les postes n'ont pas tous la même unité. Huit tests sur des lignes
fabriquées.

**L'OPEF, au passage.** Le rapport a été déposé par l'utilisateur dans le
dépôt lui-même, sous `data/brut/OPEF2026.pdf` — le seul fichier de ce
répertoire que git suive. L'action 50, menée en parallèle par une autre
session, l'avait déjà lu avec pypdf et confronté ; cette session a fait
que le lecteur PDF du dépôt le rende aussi : ses polices sont simples mais
leurs tables Unicode déclarent un espace de codes à deux octets pour des
entrées à un octet, et `lecture_pdf.py` lit désormais une police simple
par un octet quoi que sa table déclare, en traduisant par l'encodage
WinAnsi ce que la table ne dit pas. Un test de plus, et le tableau T7
rend les mêmes six valeurs par les deux lecteurs.

**Ce qui reste.** Les âges de départ des PAP, à lire dans leur tableau
enchevêtré ou à laisser saisis. 

### 52. Le pilier aux vraies moyennes du marché, et des frais qui baissent par paliers — `fait`

**Demande.** « Prends en compte tous ces chiffres dans le pilier, il faut que
l'on soit proche de la réalité pour être crédible. Par contre, on va ajouter
un critère en plus : l'évolution des frais grâce au jeu de la concurrence. Les
frais baissent au cours du temps, un peu sur le stock mais surtout sur les
nouveaux dépôts, et la baisse n'est pas forcément linéaire, elle peut être
brutale. Fais des recherches pour évaluer tous ces phénomènes. »

**Ce que la recherche a trouvé.** Partout où une épargne retraite obligatoire
existe, les frais sont tombés bien au-dessous de ceux d'un produit vendu au
détail, et par à-coups. Royaume-Uni : plafond de 0,75 % en avril 2015, 0,48 %
constatés en 2020, 0,29 % dans les régimes fiduciaires. Chili : les nouveaux
entrants sont adjugés tous les deux ans à la caisse la moins chère, et la
commission du gagnant passe de 1,14 % (2010) à 0,77, 0,47, 0,41 %, remonte à
0,69 % en 2018, puis 0,58, 0,49, 0,46 % en 2025, contre 1,36 % avant ; et une
caisse libérée de l'adjudication a remonté de 0,47 à 1,16 %. Suède : remise
imposée aux gérants, 0,31 % net en 2013, 0,21 % en 2020, 0,13 % en 2022,
0,11 % en 2026. États-Unis, où seule la concurrence joue : 1,04 % en 1996,
0,40 % en 2025 pour les fonds actions pondérés par les encours, 3,3 % de
baisse par an, et 0,76 % à 0,26 % dans les plans 401(k). Australie, plus
lente : MySuper de 1,05 à 1,00 % en 2023. France : en deux ans, le frais sur
versement du PER, mesuré sur les primes de l'année, passe de 1,20 à 1,09 %, et
celui de l'assurance-vie de 0,75 à 0,55 %, quand le frais de gestion, mesuré
sur tout l'encours, ne bouge pas : la baisse porte sur les nouveaux dépôts.
Six jeux `controle` de plus au manifeste (ICI, DWP, Superintendencia de
Pensiones et Bibliothèque du Congrès du Chili, Pensionsmyndigheten 2014).

**Ce que le modèle fait désormais.** Quatre frais aux vraies moyennes du marché
de 2025 : 1,09 % sur versement, 0,76 % sur encours, 0,99 % sur arrérages
(tous les déclarants, et non 2,20 % des seuls facturants), et 0,52 % par an sur
la réserve de la rente, le frais que l'OPEF ne mesure pas et que le CCSF
relevait sur 22 contrats sur 34 (0,60 à 1 %), estimé au milieu de la
fourchette sur la part des contrats qui facturent : 8 % de rente au diviseur du
modèle, appliqué comme une actualisation négative de la réserve, par un
facteur qui vaut exactement 1 sans frais. Chaque poste a ses paliers
`(année, taux)` dans `Parametres` : la gestion suit le rythme américain par
marches de dix ans (0,76, 0,54, 0,39, 0,28, 0,20 % en 2066, le plancher de
l'ERAFP), le versement rejoint l'assurance-vie (2031), le contrat de
capitalisation (2036) puis zéro (2046), les arrérages s'éteignent en 2046, la
réserve suit la gestion. Les lignes de l'échelle portent le tarif de leur
cohorte, gardé à chaque replacement, et referment chaque année 10 % de leur
écart avec le tarif des nouveaux dépôts (`convergence_frais_stock`) ; la
rente garde les frais de l'année où elle est souscrite. Python et portage,
témoins régénérés, cascade de la page du pilier réécrite (« de 1,09 % à 0 %
de chaque versement », une ligne pour la réserve), page Méthode, fichier de
frais avec `valeur_retenue` et `paliers`, `methodologie.md`, `limites.md`
§5 ante avec le tableau des marchés et celui des hypothèses. Sept tests de
plus.

**Ce que ça déplace.** Rien sur les scénarios 1 à 5, rien sur la répartition
du 6. Sur la rente du pilier d'une carrière entière après la bascule, + 8 %
par rapport à l'ancien réglage ; à moyennes figées elle serait 14 % plus
basse ; le stock qui garde son tarif coûte 3 %, le stock qui suit tout rend
2 %. Pour qui liquide en 2034, aucun palier n'est atteint et le frais sur la
réserve fait perdre 7 % : la réalité de 2025 est moins bonne que l'ancien
réglage pour les proches du départ, meilleure pour les jeunes.

**Ce qui reste une hypothèse.** Les paliers, datés et sourcés, ne sont pas
une mesure ; aucune série publique ne précède 2013 en Suède ni 2010 au Chili ;
le modèle ne fait jamais remonter un frais alors que le Chili l'a vu ; le
frais sur la réserve est estimé, sans mesure de l'OPEF. Tout se change en un
endroit.

### 53. Le système de frais partout où il compte : un réglage du simulateur, et le pilier de tous les cotisants sur la page Coût — `fait`

**Demande.** « Je veux que tu mettes ce système partout où cela a de
l'importance ; je pense surtout au simulateur et à la page Coût. »

**Le réglage.** Les règles du calcul portent un réglage de plus, « Frais du
pilier capitalisé », qui voyage dans l'adresse comme les autres
(`frais=…`) et s'applique partout où le pilier est calculé : simulateur,
cas types, coût. Six régimes, définis une seule fois dans
`Parametres.sous_regime_frais` et portés tels quels en JavaScript : le
marché de 2025 qui baisse par paliers (défaut) ; les mêmes paliers avec
tout le stock qui suit, un plafond ; les mêmes paliers avec un stock qui
garde son tarif, des contrats ; le marché de 2025 figé ; le PER tel qu'il est
vendu, aux 2,20 % d'arrérages des seuls facturants, sans frais de réserve ni
baisse, l'ancien réglage ; aucun frais. Un test tient l'ordre des rentes
qu'ils servent, et un autre tient les 2,20 % égaux à la valeur publiée du
fichier de frais.

**La page Coût.** Elle disait que le pilier n'est ni une ressource ni une
dépense de la répartition, et c'est toujours vrai ; elle le compte désormais
pour lui-même. `cout.py` agrège le pilier de toutes les carrières types sur
la population, comme il agrège les cotisations, à une différence près : les
cohortes voisines partagent l'année civile du pilier et non son âge, parce
qu'un pilier dépend de dates (la bascule, les paliers) et qu'une cohorte née
deux ans plus tôt n'a pas deux ans d'encours de plus en 2026. Et la règle de
la page tient : la grille ne fournit que des rapports par euro versé (frais,
encours, rentes), le niveau vient des cotisations du système 4 ancrées sur le
compte du COR, multipliées par le rapport des deux taux. Le dépliant du
pilier gagne un tableau par décennie — versements, frais prélevés, frais de
gestion en part de l'encours, encours en part de PIB, rentes servies — et
ses cumuls jusqu'en 2070 : au réglage par défaut, 6 300 Md€ collectés, 760
prélevés par l'enveloppe (12 % des versements), 3 460 de rentes servies, un
encours qui atteint 146 % du PIB. Changer le réglage change ce tableau, et
lui seul sur la page.

**Ce que ça déplace.** Rien sur le solde, la dette, la garantie ni les six
systèmes : le pilier reste hors bilan. Portage JavaScript, témoins, sept
tests.

### 54. Le bandeau sur une rangée, sans le lien vers le site du parti — `fait`

**Demande.** « Le bandeau en haut ne me plaît plus trop. Je veux enlever le
fait de revenir sur le site du Parti libéral français. De plus, il faut qu'il
soit plus élégant et en raccord avec le site. Je n'aime pas que ce soit sur
deux lignes, le titre et en dessous les pages : je préfère avec une seule
ligne. »

**Ce qui a été fait, le 20 septembre 2026.** Le lien « ← Parti libéral
français » qui coiffait le nom du site a disparu du bandeau ; la ligne de pied
« Un outil du Parti libéral français » reste le seul pont vers le site, et le
test qui imposait un pont en tête impose désormais qu'il n'y en ait aucun. Le
bandeau est une barre de 56 px : le carré d'or et le nom à gauche, les neuf
onglets à droite, sur une seule rangée dès 1 248 px de large — le nom, les
onglets et leur jour font 1 168 px. Les onglets prennent toute la hauteur de la
barre et leur filet se pose sur le filet du bandeau, si bien que l'onglet
courant s'y accroche en or comme l'onglet d'un classeur. Sous 78 rem, le nom
prend sa rangée et les onglets la leur, deux rangées de 44 px ; sous 34 rem,
la barre cesse de coller, comme avant. Les deux portages sont alignés, les
témoins de page n'ont pas bougé — ils ne comparent que le corps —, et
`docs/integration-partiliberalfrancais.md` ne promet plus de lien en tête.
Le pictogramme `arrow-left` reste dans le jeu d'icônes, sans emploi.
### 55. Les cinq points rendus sortent de la fiche de paie : le net affiché est le net plein — `fait`

**Demande.** « Je veux changer le comportement de la capitalisation
volontaire. Il faudrait afficher le salaire plein sans la capitalisation
volontaire et en même temps la compter pour la retraite. Je ne fais ça
uniquement car c'est volontaire. »

**Ce qui est fait.** La fiche de paie de la proposition s'arrête à ce que la
proposition impose : `bloc_taux_unique` ne porte plus de composante
`capitalisation_volontaire`, et le net qu'elle rend est le net plein — 18 + 5
prélevés, rien d'autre. Les cinq points rendus sont chiffrés à côté, par
`AnneeComparee.epargne_volontaire`, sur l'assiette de la proposition (la même
que le pilier), comme un **placement pris sur le net** : `net_apres_volontaire`
dit ce qui reste à qui le fait, `gain_net_apres_volontaire` l'écart avec
aujourd'hui. Le pilier, lui, ne change pas : la rente du scénario 6 compte
toujours les dix points, et sa part volontaire reste nommée à côté d'elle.
Portage `moteur/js/remuneration.js` à l'identique, témoins régénérés.

**Comment le site le montre, et pourquoi ainsi.** Le chiffre de tête du bloc
« Et pendant que vous cotisez » est désormais le net plein, et la phrase qui
le suit dit trois choses dans l'ordre : que c'est le net plein, que la rente
affichée plus haut suppose en plus les cinq points placés — « virés de votre
net sur un compte à votre nom, pas une retenue » —, et ce qu'il reste alors.
Dans le tableau, la ligne du placement est SOUS le net, avec un tiret dans la
colonne d'aujourd'hui, suivie de « restant si vous les placez » ; elle n'est
plus un « dont » du prélèvement retraite. C'est le meilleur moyen trouvé de
dire « volontaire » : une retenue est dans le brut-moins-net, un placement
est après le net, et la place de la ligne le dit avant le libellé. Le salaire
mis en regard des quatre pensions est lui aussi le net plein.

**Ce que ça déplace.** Rien sur les pensions, rien sur les six scénarios, rien
sur le coût du travail ni le brut. Pour le non-cadre du privé né en 1990, le
chiffre de tête passe de −107 € à +81 € par mois en 2026, à coût du travail
inchangé ; les 188 € du placement et les 2 782 € qui restent sont écrits
juste dessous, et la rente volontaire de 424 € par mois reste nommée sous la
barre du système 4. Cinq tests réécrits dans `test_remuneration.py` — la
fiche ne retient pas le volontaire, le placement vaut cinq points du brut
pris sur le net, le retirer ne change pas la fiche au centime —, un dans
`test_web.py` ; README et `methodologie.md` suivent.
### 56. Le partage des 23 points entre le salarié et l'employeur : le couloir, sa mesure, et le bord retenu — `fait`

**Demande.** « Je veux calculer ce qui sera le mieux en termes de répartition
des charges salariales et patronales. Je souhaite un meilleur salaire à long
terme et pas forcément sur l'immédiat ; ce serait mentir aux gens. Il faut
quelque chose de réaliste qui bénéficie premièrement les salaires. »

**Ce qui existait.** L'action 38 avait trouvé que le partage des 23 points
n'est pas neutre — −144, +73, +275 € par mois au salaire moyen selon qu'ils
sont salariaux, moitié-moitié ou patronaux — et le dépôt avait gardé
moitié-moitié, « le choix médian d'un paramètre que la proposition laisse
ouvert ». Ce chiffre était celui du seul long terme, sous l'incidence
intégrale, et il ne disait ni ce que la fiche de paie fait le lendemain de la
réforme, ni ce que le brut devient, ni qui d'autre que le salarié gagne ou
perd au passage. C'est ce que le calcul du 20 septembre 2026 ajoute.

**Le calcul.** `scripts/partage_taux_unique.py` rejoue la fiche de paie de
`remuneration.py` sous deux horizons, et les deux sont vrais : le **jour 1**,
où le brut ne bouge pas et où chacun voit sa part changer et rien d'autre
(`Incidence.ASSIETTE`), et le **long terme**, où c'est le coût du travail qui
ne bouge pas et où ce que l'employeur ne verse plus a fini par remonter dans
le brut (`Incidence.COUT_DU_TRAVAIL`, l'hypothèse du site). Quatre partages,
bornés par les deux parts d'aujourd'hui — 11,31 points sur la fiche du
salarié, 16,67 chez l'employeur, contributions d'équilibre comprises, 27,98 en
tout : **A**, la part patronale ne bouge pas et toute la baisse va au salarié
(6,33 / 16,67) ; **B**, la clé d'aujourd'hui, chaque part baisse d'un
cinquième (9,30 / 13,70) ; **C**, la part salariale ne bouge pas et toute la
baisse va à l'employeur (11,31 / 11,69) ; **D**, moitié-moitié, le défaut du
dépôt (11,50 / 11,50). En deçà de A l'employeur paie plus qu'aujourd'hui ;
au-delà de C, c'est le salarié — et D est au-delà de C. Salarié du privé non
cadre, employeur de cinquante salariés et plus, barème 2026, montants
mensuels.

**Le tableau, à deux SMIC — 3 646 € bruts, à peu près le salaire moyen.**

| Partage | Salarié / employeur | Jour 1 : net, coût du travail | Long terme : brut, net | Crédit au compte, long terme |
|---|---|---|---|---|
| A — part patronale inchangée | 6,33 / 16,67 | **+182 €**, +12 € | −0,2 %, **+175 €** | 837 € |
| B — clé d'aujourd'hui | 9,30 / 13,70 | +73 €, −89 € | +1,6 %, +122 € | 852 € |
| C — part salariale inchangée | 11,31 / 11,69 | 0 €, −157 € | **+2,9 %**, +85 € | **863 €** |
| D — moitié-moitié (défaut) | 11,50 / 11,50 | **−7 €**, −164 € | +3,1 %, +81 € | 864 € |

Au SMIC, le jour 1 donne +91 € sous A, +37 sous B, 0 sous C, −4 sous D ; et le
long terme n'y existe pas : à coût du travail fixe, le brut devrait descendre
de 2,4 à 3,4 % sous le SMIC, ce que la loi interdit, parce que la part
patronale du pilier capitalisé n'entre pas dans le périmètre de la réduction
générale et coûte à l'employeur ce que la réduction n'efface pas. Au SMIC, le
seul chiffre honnête est celui du jour 1, et seule la part salariale le fait
bouger.

**Qui paie le net du long terme.** Sous D, la retraite prélève 156 € de moins
et le salarié n'en garde que 81 : la CSG en reprend 11 et les autres branches
29, parce que le brut a monté de 3,1 % et leur assiette avec lui, et l'État
garde 35 € d'allègement qu'il ne verse plus. Plus de la moitié des cinq points
fuit. Sous A, la retraite prélève 183 € de moins et le salarié en garde 175 :
le brut n'a pas bougé, rien n'a grossi. La différence est mécanique : une
baisse de la part salariale est nette de tout, une baisse de la part patronale
remonte dans le brut, et le brut est l'assiette de la CSG (9,7 %) et de
vingt-six points de cotisations des autres branches — un quart en fuit avant
d'arriver au net, et pendant les années où elle n'est pas encore remontée,
c'est l'employeur qui la garde.

**Avec les cinq points rendus, replacés** — un placement pris sur le net depuis
l'action 55, non une retenue : sous A, ce qui reste après le placement est le
net d'aujourd'hui à un euro près (−1 € à deux SMIC), et le message tient en une
phrase — même net qu'avant, et cinq points de votre fiche deviennent un capital
à votre nom ; sous D, il manque 189 €. `--volontaire` le montre, et les deux
chiffres du défaut recoupent l'action 55 : +81 € de net plein, −107 € une fois
les cinq points placés.

**Ce que le calcul dit, en quatre points.** *Un.* La baisse de la part
salariale est la seule qui arrive le jour 1, la seule qui arrive au SMIC, et
celle qui fuit le moins ; elle ne demande aucune hypothèse d'incidence. *Deux.*
La baisse de la part patronale profite d'abord à l'employeur, puis remonte
dans le brut sur plusieurs années, et c'est la seule qui fasse monter le brut
et le crédit au compte : +2,9 % de pension et de capital sur les années
d'après la bascule sous C, contre −0,2 % sous A. *Trois.* **Le défaut du
dépôt, D, est hors du couloir** : il fait monter la part salariale de 0,19
point, et c'est le seul des quatre partages où la fiche de paie du lendemain
baisse. Il a été choisi comme milieu d'un paramètre ouvert, pas mesuré.
*Quatre.* Le partage du pilier capitalisé compte aussi : porté au seul
salarié — c'est son capital, transmissible, la même logique que les cinq
points volontaires —, avec les 18 partagés pour garder la même part salariale
totale (variantes A', B', C' du script), il retire le seul cas où le coût du
travail monte le jour 1, au SMIC.

**Ce que le calcul recommande, sous les trois critères de la demande.** Le
partage **A'** : la part patronale reste ce qu'elle est, 16,67 points, en
entier dans le périmètre de la réduction générale ; la part salariale tombe de
11,31 à 6,33 points, dont 5 vont au compte capitalisé et 1,33 à la
répartition. Réaliste : le coût du travail ne bouge pas d'un euro, à aucun
niveau de salaire, et rien ne repose sur ce qu'un employeur rendra ou ne
rendra pas. Les salaires d'abord : les cinq points arrivent en entier sur la
fiche, le lendemain, du SMIC au plafond, et ils y restent. Sans mentir : rien
n'est promis pour plus tard, parce que tout est déjà là — le « long terme » du
site n'est plus une hypothèse à défendre, c'est le même chiffre. Ce que A' ne
fait pas, et qu'il faut dire : il ne fait pas monter le **brut**. Si « un
meilleur salaire » veut dire le salaire brut — celui des indemnités, des
droits, du crédit au compte —, c'est C' qu'il faut : +3,1 % de brut et de
crédit au long terme, au prix d'une hypothèse d'incidence, d'un délai de
plusieurs années pendant lequel l'économie reste chez l'employeur, de zéro au
SMIC pour toujours, et de 94 € de net par mois de moins que A' à deux SMIC
une fois le long terme atteint. B' est entre les deux, et c'est le seul qui
donne quelque chose à l'employeur.

Une réserve sur ce que « long terme » suppose : l'incidence intégrale est
l'hypothèse standard de l'économie du travail, et pour la France les travaux
de Bozio, Breda et Grenet la trouvent pour les cotisations qui ouvrent des
droits — ce qu'est chaque euro des 18 % — et pas pour les autres. C'est une
lecture de mémoire, à confirmer sur le texte avant d'en faire une phrase du
site.

**Le programme a tranché le 20 septembre 2026 : c'est A**, et il est
implémenté. `part_salariale_taux_unique` vaut `0,0633 / 0,23`, écrit ainsi
plutôt qu'en décimal pour qu'on lise d'où il vient : 6,33 points sur 23 pour
l'assuré, 16,67 pour l'employeur, exactement ce que l'employeur verse
aujourd'hui. Les 18 % et les 5 % capitalisés suivent la même clé, 4,95 + 1,38
contre 13,05 + 3,62. A et non A' : le pilier capitalisé n'a pas son propre
partage, ce qui aurait demandé un paramètre de plus dans les deux moteurs, et
le seul cas qu'A' réglait — le coût du travail qui monte de 66 € par mois au
SMIC — est écrit dans `limites.md` plutôt que supprimé.

**Deux millièmes de point, et pourquoi on les laisse.** La part patronale
d'aujourd'hui vaut 16,6720 points et non 16,67 : l'Agirc-Arrco est à 4,7220.
Le paramètre est écrit sur le nombre rond qu'une proposition politique énonce,
si bien que l'employeur verse cinq centimes de moins par mois à un salaire et
demi le SMIC. Un test borne cet écart plutôt que de l'ignorer : s'il
grossissait, c'est qu'un taux de régime aurait bougé sans que le partage suive.

**Ce que ça déplace, et ça ne déplace aucune pension.** Le compte notionnel
porte la somme des deux parts : les six scénarios, la page Coût, la garantie,
le pilier, les témoins de simulation ne bougent pas d'un centime. Ce qui bouge
est la fiche de paie, et elle bouge partout dans le même sens. Les chiffres
ci-dessous isolent CE changement, la restitution aux salaires décidée le même
jour étant neutralisée (`part_rendue_aux_salaires=0`) : sans cette précaution
on lirait la somme des deux décisions, et surtout pas la mienne chez un
fonctionnaire, où l'autre pèse six fois plus.

| Statut, au salaire moyen | Moitié-moitié | Partage retenu |
|---|---|---|
| Salarié du privé non cadre | +73 € | **+165 €** |
| Fonctionnaire d'État | −14 € | **+166 €** |
| Agent public non titulaire | +4 € | **+96 €** |
| Artisan | +106 € | +106 € |

Gain net mensuel, euros de 2026, carrière plate liquidée à 64 ans. Au SMIC, le
salarié du privé passe de **−38 à +39 €** : le gain n'est plus négatif nulle
part, ce qui était le résultat le plus gênant de l'action 38. Le fonctionnaire
reçoit la même baisse que tout le monde, sa retenue tombant de 11,10 à 6,33
points, et l'action 38 concluait que « la proposition ne déplace presque rien
pour lui » : ce n'est plus vrai, pour deux raisons dont celle-ci est la
moindre. L'artisan ne bouge pas d'un centime, et c'est normal : il porte les
23 points en entier, le partage ne le concerne pas.

**Dans l'état du dépôt, restitution comprise**, le salarié du privé au salaire
moyen passe de +112 à **+203 €** par mois, et le fonctionnaire de +907 à
**+1 037 €** — l'essentiel de son gain vient de la moitié de la contribution
d'équilibre de l'État qui remonte dans son traitement, pas d'ici.

**Les tests que le résultat contredisait, réécrits plutôt que rendus muets.**
`test_le_gain_net_est_negatif_au_smic_et_positif_au_salaire_moyen` exigeait un
gain négatif au SMIC : il devient
`test_le_gain_net_est_positif_a_tous_les_salaires_sous_le_partage_retenu`, et
vérifie les deux horizons séparément en gardant dans son docstring pourquoi
c'était l'inverse. `test_la_proposition_ne_deplace_presque_rien_pour_un_fonctionnaire`
devient `test_le_fonctionnaire_gagne_les_cinq_points_que_le_partage_lui_rend`.
Un test neuf, `test_le_partage_retenu_laisse_la_part_patronale_ou_elle_est`,
tient la décision elle-même : il compare les deux blocs au lieu de croire le
paramètre, et c'est lui qui bornera l'écart si un taux bouge.

**Ce qui reste.** Donner à la page la ligne qui manque : le jour 1 à côté du
long terme, pour que le lecteur voie les deux chiffres et sache lequel est
promis. Le choix retenu rend cet écart plus petit qu'avant — 182 contre 175 au
salaire moyen, là où le moitié-moitié opposait −7 à +81 — mais il ne l'annule
pas, et au SMIC il reste du simple au double. Et confirmer sur le texte, avant
d'en faire une phrase du site, la réserve ci-dessus sur l'incidence.

**Fichiers.** `scripts/partage_taux_unique.py` ;
`part_salariale_taux_unique` dans `config.py` et `config.js` ; le docstring du
module et le défaut de `bloc_taux_unique` dans `remuneration.py`, et son
portage `moteur/js/remuneration.js` ; `_salaire_net_partage` dans
`web/pages.py` et `moteur/js/pages.js` ; trois tests de
`tests/test_remuneration.py` ; `docs/limites.md` § 5 ante bis, réserves 2 et 3 ;
témoins régénérés.

### 57. Le total du système 4 est annoncé comme un plafond : « retraite jusqu'à », et le plancher sous lui — `fait`

**Demande.** « Est-ce qu'on peut changer la retraite montrée pour le système 4
par la répartition, la capitalisation obligatoire et facultative ? Pour ne pas
mentir, on peut dire jusqu'à xxxx €/mois sans risque. Ça ne ment pas et ça
peut montrer le gain potentiel d'une capitalisation facultative de 5 % sans
risque. »

**Ce que l'action 55 avait ouvert.** Depuis qu'elle a sorti les cinq points
rendus de la fiche de paie, la ligne du système 4 montrait le salaire de qui
ne place RIEN — le net plein — à côté de la pension de qui place TOUT : le
total comprend la rente volontaire, et la comprenait déjà. Les deux chiffres
sont vrais séparément et se contredisent ensemble. C'est cet écart que la
demande nomme, et sa réponse est la bonne : un plafond n'est pas un mensonge
tant qu'il est dit plafond.

**Ce qui est fait.** Le grand nombre du système 4 porte désormais l'étiquette
« RETRAITE JUSQU'À » au lieu de « RETRAITE », et lui seul — les trois autres
systèmes ne dépendent d'aucune décision de l'assuré, et leur étiquette ne
bouge pas. La ligne de composition sous lui passe de trois montants à quatre,
avec le PLANCHER écrit au milieu : pension par répartition, plus rente
capitalisée obligatoire, « soit X par mois sans rien ajouter », puis « et Y de
plus si vous placez les cinq points rendus, sans risque ». La glose dit que
les deux cotisations capitalisées sont « les unes comme les autres placées
sans risque ». Sans le volontaire (`capitalisation_volontaire=False`),
l'étiquette et la ligne retrouvent leur forme d'avant : rien de tout cela ne
paraît.

**Pourquoi « sans risque » ne se paie pas de mots.** C'est le placement que le
modèle applique déjà, écrit sur la page Méthode et dans `methodologie.md` :
des titres d'État portés jusqu'à leur échéance, sur la courbe des taux sans
risque de la zone euro, à des maturités qui raccourcissent à l'approche du
départ. C'est ce qui autorise le mot « jusqu'à » plutôt qu'une fourchette : le
montant du haut s'atteint par une décision, pas par un coup de bourse. Le
modèle ne simule aucun risque de marché, et la page le dit déjà.

**Ce que ça déplace.** Aucun chiffre : ni le total, qui comprenait déjà la
rente volontaire, ni la répartition, ni le taux de remplacement, ni l'écart au
système actuel. Ce qui change est ce que le lecteur croit lire. Pour le
non-cadre du privé né en 1990 à 3 000 € par mois, la ligne annonce « jusqu'à
1 981,34 € », écrit « 1 663,91 € par mois sans rien ajouter » et « 317,43 € de
plus si vous placez les cinq points rendus ». Portage JS à l'identique,
témoins régénérés, rendu vérifié sans débordement à 1440, 1024 et 390 points ;
le test des cinq points volontaires exige l'étiquette, son unicité, le
plancher et la condition ; README, `methodologie.md` et le parcours de
présentation suivent.
### 58. L'allocation des maturités : le pilier s'adosse à la date du départ — `fait`

**Demande.** « J'aimerais jouer un peu plus sur la retraite par capitalisation.
Il faudrait que l'on choisisse un peu mieux l'allocation des différents taux
sans risque pour avoir une meilleure retraite par capitalisation. »

**Ce qu'on a trouvé en cherchant, et qui règle la question avant de commencer.**
L'échelle de maturités du pilier — 2, 10 et 30 ans, glissant du long vers le
court, aucune ligne au-dessus de trois quarts — **n'avait aucun effet sur le
résultat**. Pas « peu » : aucun, au centime. C'est une identité, et elle tient
en une ligne : sous l'hypothèse des anticipations pures, qui est celle du
modèle, découper `[t, T]` en un trente ans, en trois dix ans ou en quinze deux
ans accumule exactement `exp(z(T)·T − z(t)·t)`, parce que c'est ce que
l'arbitrage impose au forward. Les frais annuels n'y changent rien non plus :
un prélèvement de `g` multiplie une ligne par `(1 − g)` autant de fois qu'elle
passe d'années dans l'enveloppe, et ce compte-là ne dépend pas du découpage.
Vérifié à la main sur quatre règles que tout sépare, puis figé en test.

Accorder l'échelle était donc du temps perdu d'avance. Ce qui pouvait être fait,
et qui l'a été, tient en deux pièces.

**1. L'adossement à l'horizon remplace le glissement.** Chaque versement achète
une seule maturité, `min(h, 30)` : celle qui arrive à échéance l'année du
départ, plafonnée au bout de la courbe publiée. Les trente maturités de la BCE
étant toutes cotées, rien n'est interpolé. La raison n'est pas le rendement,
c'est le risque : le compte doit un capital à une **date**, et l'actif sans
risque d'une dette datée est le zéro-coupon qui tombe ce jour-là. Raccourcir à
l'approche du départ est le réflexe d'un portefeuille d'actions, dont le prix de
vente est incertain ; ce compte ne vend rien, il attend. Ce dont il avait à se
protéger était le taux de chaque replacement, et c'est l'échelle elle-même qui
le créait. L'adossement le ramène à zéro sous trente ans d'horizon, et à un
seul replacement au-delà.

**2. La prime de terme devient un paramètre, à zéro.**
`Parametres.prime_terme_trente_ans` décompose le taux observé en `z = z* + φ(m)`,
calcule les forwards sur `z*` et rajoute la prime de la maturité **achetée** :
à différé nul on retrouve donc exactement le taux coté du jour, et seul ce qui
n'est pas encore acheté est corrigé. C'est le seul réglage sous lequel
l'allocation pèse, et c'est la réserve n° 1 des limites du pilier — la prime de
terme non retirée des forwards — qui devient mesurable au lieu d'être seulement
dite. **Le site continue de publier à zéro** : mettre un chiffre par défaut
serait remplacer une hypothèse par une autre, et c'est une décision, pas une
correction.

**Ce que ça déplace.** Rien, et c'était prévisible : capital et rente identiques
au centime sur les 491 simulations témoins. Seule bouge l'espérance de capital
transmis, +0,19 %, parce qu'elle seule dépend des encours **intermédiaires** —
bloquer la maturité longue dès le premier versement fait valoir le compte un peu
plus cher en milieu de carrière. La décomposition annuelle intérêts / frais se
déplace aussi, à somme constante.

Ce que l'allocation vaut se lit en revanche dès que la prime n'est plus nulle. À
`prime_terme_trente_ans = 0,005`, milieu de la fourchette que la littérature
retient, sur une carrière de trente-six ans partant en 2060 : l'adossement rend
1,6 % de capital de plus que l'échelle glissante (7 € de rente mensuelle) et
6,2 % de plus qu'un roulement à un an. Et le même réglage retire 4,8 % au pilier
par rapport à ce qui est publié aujourd'hui, soit 23 € de rente par mois : la
prime de terme coûte trois fois ce que la meilleure allocation rapporte. Le
dire dans cet ordre est la seule façon honnête de le dire.

**Ce qui restait ouvert, et comment c'est tranché.** Le chiffre par défaut de
`prime_terme_trente_ans` : à zéro le site reste sous les anticipations pures,
hypothèse explicite, vérifiable et flatteuse ; à 0,005 le pilier devient plus
défendable et plus bas. Plutôt que de trancher pour le lecteur, le paramètre
est devenu un **réglage du site**, « Taux futurs du pilier capitalisé », à côté
de celui des frais, à trois positions : les taux à terme de la courbe (défaut,
zéro), la prime retirée au milieu de la fourchette (0,50 point à trente ans),
la prime retirée au haut (1 point). Il voyage dans l'adresse, s'applique au
simulateur comme aux pages qui agrègent, et `Parametres.sous_regime_taux` le
définit une fois pour les deux portages.

C'est le seul endroit d'où l'on voie que l'allocation des maturités ne vaut
rien sous le réglage par défaut : qui bascule sur `prime` voit la rente baisser
— c'est le prix de l'hypothèse — et voit du même coup apparaître l'écart entre
l'adossement et un roulement, qui était nul l'instant d'avant. Une réserve
qu'un lecteur peut chiffrer lui-même cesse d'être une réserve qu'on lui demande
de croire. Aucun chiffre publié ne bouge : le défaut est inchangé.

### 59. Les impôts que la proposition n'encaisse plus sont rendus pour moitié aux salaires, et pour moitié à la dette — `fait`

**Demande.** « Je veux que l'on enlève certains impôts et taxes du salaire.
Effectivement, on a enlevé les impôts et taxes affectées ainsi que les
contributions de l'État. Il ne faut pas que ces baisses d'impôts servent
uniquement à combler le déficit. Il faut aussi que les salaires soient
augmentés. »

**Ce que la lecture du droit a trouvé, et qui a changé la question.** Avant de
rendre un impôt « du salaire », il fallait savoir lesquels, dans le poste
« impôts et taxes affectés », sortent d'un salaire. L'index LEGI du dépôt
répond, et la réponse est l'inverse de ce qu'on attendait.

**La CSG sur les revenus d'ACTIVITÉ ne finance aucune retraite.** Ses 9,20
points se répartissent, à l'article L. 131-8, 3° du code de la sécurité
sociale dans sa rédaction en vigueur depuis le 1er février 2026 : Caisse
nationale des allocations familiales 0,95, régimes obligatoires d'assurance
maladie 4,25, Caisse d'amortissement de la dette sociale 0,45, Unédic 1,47,
Caisse nationale de solidarité pour l'autonomie 2,08. Neuf virgule vingt
exactement, et rien pour la branche vieillesse. Ce que la retraite encaisse en
CSG est assis sur le capital (6,67 points sur 10,6, L. 131-8, 3° bis) et sur
les pensions (2,94 points, L. 131-8, 3° e). Supprimer « la CSG retraite » de la
fiche de paie n'avait donc aucun sens : elle n'y est pas.

**Deux impôts du poste seulement sortent d'une rémunération.** La taxe sur les
salaires, dont L. 131-8, 1° verse 58,35 % à la branche vieillesse — une
fraction que la LFSS pour 2026 a fait passer de 63,25 à 58,35 % —, et le
forfait social, dont L. 241-3, 1° donne le produit ENTIER à l'assurance
vieillesse. Le compte de la CNAV les chiffre : 9 694 et 6 300 M€ en 2024,
ensemble 28 % du poste.

**Ce qui a été décidé.** Le partage, et il vaut deux fois :

    la moitié est rendue aux salaires, la moitié éteint de la dette.

`Parametres.part_rendue_aux_salaires`, à 0,5, et zéro rend l'ancienne
convention, ce qu'un test vérifie. Premier volet, les impôts affectés : on
supprime d'abord la taxe sur les salaires et le forfait social, puis le solde
de la moitié rendue revient par une baisse de la CSG d'activité — 1,12 point en
2026, 32 Md€ rendus, 32 éteints. Second volet, la contribution d'équilibre d'un
employeur public : 82,28 % du traitement d'un fonctionnaire d'État en 2026,
ramenés à la part patronale du taux unique, et la moitié de ce qui est libéré
remonte dans le traitement. C'est `Incidence.PARTAGEE`, une troisième valeur à
côté de l'incidence intégrale et de l'assiette fixe, et elle dit à quoi sert
l'argent au lieu de choisir un bord.

**Ce que ça déplace, sur la fiche de paie de 2026.** Le non-cadre au SMIC perd
1,26 % au lieu de 2,61 % — le résultat reste négatif, la réduction générale
effaçant déjà toute la part patronale à ce niveau. Le cadre à 2,5 SMIC gagne
4,91 % au lieu de 3,47 %. Le fonctionnaire d'État gagne **32,9 %** — à tous les
niveaux de traitement, ni réduction générale ni plafond ne courbant le calcul —,
contre rien du tout auparavant : c'est le second volet, et de loin
le plus lourd. **Aucun solde du système de retraite ne bouge d'un centime** :
ces recettes en étaient déjà sorties, et ce que la décision ajoute est ce
qu'elles deviennent.

**La série qu'il a fallu certifier.** `scripts/fetch/ccss_impots_retraite.py`
lit la taxe sur les salaires et le forfait social dans la section CNAV de la
fiche « contributions sociales et recettes fiscales brutes » des rapports à la
Commission des comptes de la Sécurité sociale. La SECTION compte : « taxe sur
les salaires » figure une fois par branche dans le même tableau, et prendre la
première ligne donnerait la part de la branche maladie. La série commence en
2019 parce que le fonds de solidarité vieillesse recevait jusque-là sa propre
fraction de ces deux impôts, et que depuis le 1er janvier 2019 l'article
L. 135-3 ne lui laisse que de la CSG : quatorze valeurs au niveau `haute`,
2019-2025. Au-delà, c'est la PART DU POSTE qui se reconduit — 26,6 à 28,9 %
depuis 2019 — et non le montant, pour la même raison que l'assiette.

**Ce qui reste, et c'est écrit.** Deux manques, sous `limites.md` § 5 ante bis
et § 5 ante quater. La suppression de la taxe sur les salaires ne se voit sur
aucune fiche du modèle : elle n'est due que par les employeurs non assujettis
à la TVA — hôpitaux, banques, associations —, et le profil d'employeur du dépôt
est une entreprise assujettie. Le dépôt COMPTE cette suppression dans
l'enveloppe, il ne la RÉPARTIT sur personne. Et la pension reste calculée sur le
revenu de la carrière, pas sur le brut que la fiche affiche : pour un agent
public dont le traitement monte d'un tiers, le dépôt sous-estime désormais sa
propre proposition d'autant. Le corriger demanderait de reboucler la fiche sur
la carrière, ce qui est un point fixe et non un calcul de plus.

**Et le partage est un état d'arrivée, pas un calendrier.** La demande le dit
elle-même — « les entreprises vont augmenter au fur et à mesure les salaires ».
Une baisse de CSG salariale tombe sur le net le mois suivant ; la suppression
d'un impôt payé par l'employeur ne remonte dans les salaires que par la
négociation, au fil des années. Le modèle montre le RÉGIME PERMANENT, ce qui
est exactement l'hypothèse d'incidence qu'il assume déjà pour les cotisations
patronales. Rien ne dit en combien d'années, et rien ne le mesure.

**Ce qui n'est vérifié par rien.** La moitié qui « éteint de la dette ». Le
dépôt ne modélise aucun budget de l'État : cette moitié est une affirmation du
programme, pas un résultat du modèle, et rien ne tomberait en défaut si elle
était fausse.
### 61. « Au premier euro et sans plafond », sans exception — `fait`

**Pourquoi.** Ouverte par le catalogue des affirmations (action 34), qui l'a
trouvée en cherchant ce que le code dément. L'accueil promet, en deuxième
geste du calcul : « On inscrit chaque cotisation sur votre compte, au premier
euro, sans plafond » ; la page Méthode redit « au premier euro et sans
plafond ». Le modèle, lui, porte `plafond_assiette_en_pass = 8.0`
(`config.py`) : au-delà de huit plafonds de la Sécurité sociale, rien n'entre
plus au compte. À dix fois le salaire moyen — le plus haut revenu que le
formulaire accepte — l'assiette retenue vaut 86 % du revenu en 2030 et 81 %
en 2053, le plafond progressant moins vite que le salaire saisi. Personne ne
le lit nulle part : ni la page de résultats, ni le dépliant du détail, ni la
page Méthode ne disent qu'un revenu peut sortir de l'assiette.

**Ce que ce n'est pas.** Ce n'est pas la règle d'un régime : les fiches
portent leurs propres bornes, et celle-ci est un paramètre de SIMULATION,
posé au-dessus d'elles. C'est pourquoi la phrase n'est pas simplement fausse :
elle décrit la proposition, qui ne veut pas de plafond, et le modèle en pose
un que rien n'oblige.

**Trois issues, et il faut trancher.**

1. *Le paramètre passe à `None` après la bascule.* La proposition dit
   « déplafonné », le régime fusionné dit `assiette: deplafonnee` : le
   modèle suivrait alors ce qu'il affirme. Coût : les hauts revenus voient
   leur capital notionnel monter, leur pension avec, et la recette du
   système 4 aussi — à chiffrer, c'est le seul des trois qui déplace des
   nombres.
2. *La phrase se borne.* « Au premier euro, et sans plafond jusqu'à huit
   fois le plafond de la Sécurité sociale » : exact, plus long, et cela
   avoue une limite du modèle au milieu d'une promesse politique.
3. *La page le dit là où ça se voit.* Le paramètre reste, la phrase reste,
   et la page de résultats affiche, quand l'assiette d'une année a été
   rognée, de combien elle l'a été — comme elle affiche déjà
   l'avertissement d'ouverture.

**Ce qui a été tranché : l'issue 1**, le paramètre à `None`. C'est la seule
qui rende la phrase vraie, et c'est aussi celle que le modèle réclamait : sa
doctrine de fusion dit « assiette : la plus large — tout revenu cotise », et le
catalogue disait les deux choses à la fois — `accueil.transition_regime_unique`
vérifiée sur la fiche déplafonnée du régime unique, `accueil.on_inscrit`
contredite sur le paramètre qui la démentait.

**Ce qu'il fallait mesurer avant, et que la note demandait.** Le plafond ne
mordait qu'APRÈS la bascule : sur la carrière la plus haute du formulaire, 28
années rognées, 2026 à 2053, et pas une avant — jusque-là ce sont les bornes
des fiches qui rognent, et c'est le droit. Le seuil est 8 PASS, soit 9,22 fois
le salaire moyen, un rapport stable dans le temps : 32 040 € par mois en 2026.
En deçà de 8 fois le salaire moyen, lever le plafond ne change pas un centime ;
à 9 fois, la pension monte de 5 % ; à 10 fois, de 14,1 % au système 2, 13,8 %
au 3 et 12,4 % au 4.

**Et ce que la note redoutait n'existe pas.** « La recette du système 4 aussi —
à chiffrer » : le coût agrégé, le solde et les coefficients d'équilibre sont
IDENTIQUES AU CENTIME avec et sans le plafond, sur les quatre systèmes et tout
l'horizon. La grille des cas types plafonne à 2,5 fois le salaire moyen, et
personne n'y gagne assez pour être concerné. Ce n'est pas une bonne nouvelle,
c'est une limite qui se voit enfin : elle est écrite sous `limites.md` § 5 bis,
cinquième approximation, et dans l'en-tête de `cout.py`.

**Fichiers.** `config.py` et `moteur/js/config.js` (le paramètre, `None` des
deux côtés), `tests/test_affirmations.py` (le contrôle retourné, devenu
`assiette_deplafonnee_apres_la_bascule`), `affirmations.yaml`
(`accueil.on_inscrit` passée en `verifiee`, et la phrase jumelle de la page
Méthode y prend sa ligne), `scripts/construire_temoins.py` (un témoin à dix
fois le salaire moyen : c'est le seul niveau qui franchisse l'ancien plafond,
et c'est lui qui tient les deux moteurs d'accord), `limites.md` et `cout.py`
(la limite de la grille). Aucune phrase du site n'a changé : elles étaient
justes, c'est le modèle qui ne les suivait pas.

---

### 62. Le scénario 1 cesse d'être trop beau pour être vrai — `fait`

**Demande.** « J'aimerais traiter le scénario 1 comme un scénario qui va
changer. En l'état actuel, le scénario 1 est trop beau pour être vrai. Il y a
un système qui est en déficit par construction. Je ne trouve pas ça honnête de
dire qu'on va garder des salaires hauts et des retraites hautes pour les gens
qui ne sont pas encore à la retraite. Est-ce qu'il y a moyen de montrer cela
sans mentir au visiteur du site ? »

**Ce qui a été fait.** La réponse tenait dans un chiffre que le dépôt
calculait déjà, depuis l'action 6, sans jamais l'afficher à côté d'une
pension — le coefficient d'équilibre, 0,99 en 2026 et 0,84 en 2070. Le montant du système 1 n'a pas
bougé d'un euro, et ne devait pas bouger : il est le droit en vigueur, c'est
sa définition. À côté de lui, un troisième chiffre dit ce que les recettes du
système en paient, avec le manque EN EUROS sous lui ; la barre montre la part
qui manque ; et un dépliant nomme qui paiera la différence.

**La décision qui a coûté le plus à trancher** est de l'appliquer aux QUATRE
systèmes et non au seul scénario 1. Le contraire aurait flatté la
proposition, dont le coefficient est plus bas que celui du système actuel sur
la plus grande partie de l'horizon — 0,79 contre 0,90 en 2054. Symétriquement,
un coefficient supérieur à un n'est jamais converti en euros : les systèmes 2
et 3 encaissent deux à trois fois ce qu'ils versent, et écrire « financé :
927 € » sous une pension de 265 € ferait promettre ce que personne n'a décidé
de servir. La marge est dite en toutes lettres.

**Ce que ça déplace :** aucune pension calculée. Le portage JavaScript rend
le même HTML que le Python, témoins compris, et les 491 simulations sont
identiques au centime. Ce qui bouge est le poids du paquet — le bilan figé
pèse 40 Ko — et le test de péremption du paquet, qui coûte désormais les
dix-huit secondes du coût agrégé ; il reçoit le contexte du module pour ne
pas les payer deux fois.

**Écrit deux fois, et c'est la seconde version qui compte.** La première
ouvrait sur le coefficient d'équilibre et deux tableaux de nombres sans
dimension — 0,90 puis 0,87, des points d'assiette, des parts de PIB. Retour de
l'utilisateur : « c'est pas très clair pour un électeur moyen ». Il avait
raison, et le défaut n'était pas le fond mais l'unité : personne n'a de repère
pour « 3,5 points d'assiette », tout le monde en a un pour « 122 € de plus
prélevés chaque mois ». Trois corrections en sont sorties.

- **Le manque est écrit en euros, sous le chiffre**, dans l'idiome que l'écart
  de salaire utilisait déjà : « il manque 393 € par mois ». C'est ce que le
  lecteur retient ; « 87 % » est une proportion, une somme se compare à un
  loyer.
- **Les trois leviers sont nommés par QUI paie**, et chiffrés dans les unités
  où on les vit : les retraités (pensions rognées de 10 %), les actifs (122 €
  de plus prélevés chaque mois sur un salaire moyen), ou personne pour
  l'instant (44 milliards empruntés par an). Une liste de trois phrases, et non
  plus un tableau de trois colonnes qui laissait au lecteur le soin de
  comprendre qu'il s'agissait du même trou. La conversion en euros a demandé
  deux étalons, tous deux écrits sur la page : le salaire moyen brut
  d'aujourd'hui, exact parce que le prélèvement est proportionnel, et le PIB de
  la dernière année publiée, la table figée le portant désormais — un PIB de
  2054 serait une hypothèse de croissance déguisée en observation.
- **Le tableau des coefficients est descendu d'un cran**, sous un dépliant
  imbriqué, avec ses colonnes en pourcentages avant de l'être en coefficient.
  Rien n'est retiré, tout est rangé par ordre de lisibilité.

**Deux choses trouvées en chemin.** La clé de lecture promettait encore « deux
chiffres par ligne » au-dessus de trois — un test l'exige maintenant. Et les
nombres mis en gras échappaient au catalogue des affirmations, qui ne peut
tenir que des phrases stables : le gras est désormais réservé aux phrases, et
les cinq qui portent une affirmation ont leur ligne au catalogue.

---

### 63. Les barres 2 et 3 de Simuler nomment ce que le lecteur a cotisé — `fait`

**La demande.** « Il faudrait dire en gros "ce que vous avez cotisé avec la
part salariale" et "ce que vous avez cotisé avec la part salariale +
patronale" pour les scénarios 2 et 3. » Les titres disaient « Compte
notionnel, part salariale seule » et « Compte notionnel, part salariale +
patronale » : ils nommaient l'assiette sans dire qu'elle est ce que le lecteur
a versé, et il fallait savoir qu'un compte notionnel est alimenté par les
cotisations pour lire l'écart entre les deux barres — qui est, exactement, ce
que l'employeur verse.

**Ce qui a été fait.** `_titres_scenarios` et les gloses de la page Simuler,
dans `web/pages.py` et son portage `moteur/js/pages.js` : « 2. Ce que vous
avez cotisé, part salariale seule », « 3. Ce que vous avez cotisé, part
salariale + patronale ». Les mêmes titres portent la légende du graphique de
trajectoire, qui est sur la même page. Témoins régénérés, `test_web.py` suit.

**Ce qui n'a pas bougé, et pourquoi.** `LIBELLES_SYSTEMES` — les libellés
courts des tableaux de Coût, des grilles de Cas types et des légendes de leurs
graphiques — garde sa forme impersonnelle (« 2. Compte notionnel, part
salariale », « 3. Compte notionnel, les deux parts »). Ces pages montrent les
carrières d'autres gens et une dépense nationale : le « vous » y désignerait
quelqu'un qui n'est pas le lecteur. Simuler est la seule page où la carrière
affichée est la sienne.

**Au passage.** La phrase « Notre système ne sert aucune réversion », posée sur
l'accueil la veille, échappait au catalogue des affirmations et laissait
`test_rien_n_echappe_au_catalogue` rouge avant cette session. Elle y prend sa
ligne (`accueil.pas_de_reversion`), sous le contrôle qui vérifie déjà la même
affirmation sur la page Coût.

---

### 64. Deux phrases que le site disait faux, et l'action 11 archivée — `fait`

**Demande.** « Archive l'action 11, je ne veux plus la voir. Corrige les
autres problèmes. » Faisait suite à une revue où trois points avaient été
relevés, dont un qui s'est révélé faux à la vérification.

**Ce qui était faux dans ma propre revue, et il faut le dire en premier.**
J'avais annoncé que la page Cas types portait le même défaut que le
simulateur avant l'action 62 : des pensions présentées comme acquises. C'est
inexact, et il suffisait de rendre la page pour le voir. Cas types n'affiche
AUCUN montant, seulement des écarts en pourcentage d'un système à l'autre, et
elle porte déjà en tête une note sur le déficit du système actuel, chiffrée.
Il n'y avait rien à y ajouter de ce côté.

**Le vrai défaut, trouvé en cherchant l'autre.** Cette note disait que le
coefficient d'équilibre « multiplierait les cases par le même facteur ». La
phrase est fausse deux fois. Un facteur COMMUN laisserait ces cases
inchangées, une case étant déjà un rapport de deux pensions, où un facteur
commun se simplifie. Et il n'y a pas un facteur mais quatre : chaque système a
le sien, et les ramener chacun à son équilibre déplacerait les écarts du
rapport de ces coefficients. Mesuré plutôt qu'affirmé : **12 points en médiane
sur les 80 cases de la grille**, et bien plus sur les générations déjà
liquidées, où la proposition encaisse plusieurs fois ce qu'elle verse.

**Ce que le catalogue des affirmations n'avait pas rattrapé.** La phrase y
était, à l'état `verifiee`, sous le contrôle `coefficient_jamais_applique` —
qui vérifie que le coefficient n'est pas appliqué, c'est-à-dire tout autre
chose que ce que la phrase affirmait. Un contrôle qui ne teste pas sa phrase
est pire qu'absent : il la déclare tenue. Elle porte désormais
`les_ecarts_bougent_si_chaque_systeme_s_equilibre`, qui mesure ce qu'elle dit.

**Deux pourcentages qui se lisaient tous deux « non financé ».** La page
Risque affiche côte à côte 34 % et 16 %. Le premier compare UNE PENSION à ce
que les cotisations de cet assuré achèteraient, le second LES DÉPENSES du
système à ses recettes. Rien de contradictoire, les deux sont justes, mais
rien n'interdisait de les additionner. Les deux libellés le disent maintenant,
et une phrase sous les chiffres l'interdit.

**Le budget de lecture a commandé la forme.** Cas types était exactement à son
plafond de 750 mots : toute phrase ajoutée devait en retirer une autre. Ce qui
corrige l'affirmation reste donc visible, ce qui l'explique est passé sous une
bulle. C'est l'idiome du dépôt, et il valait mieux que de rogner ailleurs.

**Action 11, archivée.** Le pilotage de l'agrégat descend dans « Ce qui est
délibérément en bas », avec ce qu'il aurait demandé et le fait qu'il laisse
trois phrases du site à l'état `contredite` sans plus rien pour les refermer.
Sa section ne peut pas disparaître tout à fait : ces trois entrées du
catalogue nomment l'action, et un test exige qu'elle existe. Il en reste un
paragraphe qui dit où est passé le reste.

---

### 65. L'assiette projetée était une déduction, et le COR publie la réponse — `fait`

**Demande.** « Est-ce que les recettes et les dépenses par rapport au PIB du
système de retraite correspondent à l'état de l'art de la comptabilité ? »
Puis, sur l'audit qui a suivi : « fais le lot 1+2 ». Deux corrections, donc :
l'assiette projetée, et le dénominateur.

**Ce qui n'allait pas, et ce n'était pas une erreur de calcul.** La recette de
la proposition est 18 % d'une assiette. Sur les années publiées, c'est une
mesure ; au-delà, il faut dire ce que l'assiette devient. Les ressources que le
COR projette reculent en part de PIB — 13,95 % en 2025, 12,91 % en 2070 — et ce
recul se partage entre un taux qui baisse et une assiette qui rétrécit, sans que
les deux colonnes du compte disent lequel. Le dépôt reconduisait le taux du bord
et faisait donc porter TOUT le recul à l'assiette, qui tombait de 42,5 % du PIB
à 39,3 %. Il s'en justifiait dans `assiette.py` : « c'est le COR qui tranche ».

C'était une déduction tirée du total de ses ressources, et elle le tranchait à
l'envers. Deux choses la démentaient, dont une dans le dépôt même :
`hypotheses_projection.yaml` refuse explicitement de « projeter une déformation
du partage de la valeur ajoutée », et 42,5 → 39,3 % en est une, de 7,4 %. Le
dépôt se contredisait d'un fichier à l'autre, et personne ne l'avait vu parce
que les deux phrases sont à deux cents lignes l'une de l'autre.

**Ce que le COR publie, et que trois passes de récupération n'avaient pas
cherché.** La figure « Les déterminants de l'évolution des ressources du système
de retraite », partie 2 du rapport annuel, porte le TAUX DE PRÉLÈVEMENT en part
des revenus d'activité, observé de 2002 à 2025 et projeté jusqu'en 2070. Il
baisse : 32,14 % à 30,05 %. C'est donc le taux qui explique le recul des
ressources, et l'assiette tient sa part de PIB à un point près — l'inverse de ce
que le dépôt supposait. `taux_prelevement_retraite.csv` la porte, au même
niveau `haute`/`projetee` que les deux colonnes du compte.

**Le profil, jamais le niveau.** « Revenus d'activité » chez le COR n'est pas
l'assiette d'`assiette_activite.csv` : 32,14 % contre 32,84 % mesuré ici en
2025, 2 % d'écart. Le dépôt garde SA mesure pour l'année d'ancrage, la seule
qu'il certifie, et n'emprunte que le rapport d'une année projetée à celle-là
(`ComptesRetraite.profil_taux`). Le profil vaut un sur toute année publiée : les
années observées ne bougent pas d'un centime, et un test l'exige.

**Ce que ça a déplacé.** Le solde de la proposition gagne **0,49 point de PIB en
2070**, 0,28 en moyenne sur 2026-2070 : moyenne projetée de −1,52 à −1,24 point,
2070 de −0,63 à −0,14, coefficient d'équilibre 2070 de 0,92 à 0,98. Les années
proches bougent à peine, et 2030 bouge dans l'AUTRE sens — le COR fait monter son
taux jusque-là. Une série lue ne va pas toujours dans le sens qui arrange, et
c'est ce qui la distingue d'une hypothèse.

**Le lot 2, qui n'était pas celui qu'on croyait.** L'audit proposait de stocker
les deux colonnes du COR en euros pour recalculer leurs parts contre un seul
PIB. Vérification faite, le COR **ne publie pas ses comptes en euros** : ses
figures sont en part de PIB, et le dépôt ne peut pas les rebaser. La note de
ces figures dit en revanche la base du dénominateur — « comptes nationaux de
l'Insee base 2020 », celle de `pib_courant.csv`. Le lot 2 est donc devenu deux
autres choses.

**Un contrôle de base, en euros, une fois par rapport.** Le COR publie une fois
par rapport la structure de ses ressources EN MILLIARDS : 422,2 Md€ en 2025,
dont 5,6 de produits financiers que la convention du compte exclut. Les 416,6
restants sur un PIB de 2 991,1 Md€ font 13,93 %, contre 13,95 % publiés — deux
centièmes de point. `controle_base_comptable_retraite` tient ce recoupement sur
toutes les années où le COR donne un total en euros, et c'est lui qui
s'apercevrait qu'un rapport a changé de base sans le dire. Sans ce contrôle, le
recoupement des deux périmètres — trois dixièmes de point entre la DREES et le
COR, le seul contrôle externe de ces séries — pouvait être en partie un effet de
base, et ne rien dire.

**Le troisième PIB projeté, supprimé.** Le dépôt en portait trois : celui de
l'indexation (`macro.pib_nominal`, rythme du COR composé avec sa trajectoire
d'emploi), celui qu'implique le compte du COR, et celui que la page Coût se
fabriquait — le rythme du COR corrigé par la population des **20-64 ans**, qui
recule de 10 % quand l'emploi projeté par le COR recule de 6 %. Ce proxy avait
été posé contre une hypothèse d'emploi constant que l'action 46 a supprimée ; il
lui a survécu quelques jours. La page lit maintenant `macro.pib_nominal`, et
`pib_nominal_hors_emploi` disparaît des deux portages, n'ayant plus de lecteur.

**Ce que ça a déplacé.** La trajectoire 2070 du système actuel passe de 19,4 à
**18,35 % du PIB** — 1,05 point, du dénominateur seul, aucune pension n'ayant
bougé. L'écart au COR, que `limites.md` § 5 ter chiffrait à cinq points, en
valait donc un de dénominateur : il est de trois points contre les 15,3 % que le
rapport de juin 2026 projette. Les 469 témoins de simulation n'ont pas bougé
d'un bit dans les deux corrections réunies : elles ne touchent aucune pension,
seulement ce que les comptes en financent et ce à quoi on les rapporte.

**Ce qui reste ouvert, et qui demande un arbitrage.** Le PIB reste UNIQUE PAR
ANNÉE, commun aux six systèmes — c'est ce qui rend leurs courbes comparables, et
c'est aussi une hypothèse, puisque la trajectoire d'emploi ne s'applique qu'aux
systèmes 2 à 6. Un système qui déplacerait réellement l'emploi déplacerait son
dénominateur, et la page ne sait pas le montrer. Et le taux emprunté au COR
décrit le système ACTUEL : un système à 18 % sans exonération, sans plafond et
sans tranche n'aurait pas la même assiette. Le dépôt emprunte la forme d'une
trajectoire à défaut de savoir produire la sienne.

**Trois écarts de l'audit qui n'ont pas été traités, et qui restent.** La
convention EPR est écrite dans les en-têtes de données et dans `sources.yaml`,
et nulle part dans la prose du site : sous cette convention, la contribution de
l'État au régime de ses fonctionnaires est un solde endogène, et le déficit
affiché est donc un déficit APRÈS que l'État a bouclé la fonction publique. Le
COR publie la convention EEC en données complémentaires de la même figure, et le
dépôt pourrait montrer les deux. Le brut et le net ne sont pas distingués — les
2,94 points de CSG assis sur les pensions sont une recette qui est une fraction
de la dépense. Et le dépôt ne porte aucun engagement de retraite ACQUIS À DATE,
alors qu'un modèle en comptes notionnels le produit nativement : la somme des
capitaux virtuels est cette grandeur, celle que le tableau supplémentaire du
SEC 2010 demande.

**Fichiers.** `scripts/fetch/cor_comptes_retraite.py`, `scripts/verifier_donnees.py`,
`data/reference/macro/taux_prelevement_retraite.csv`, `data/sources.yaml`,
`donnees/equilibre.py`, `donnees/assiette.py`, `donnees/macro.py`, `cout.py`,
`moteur/js/equilibre.js`, `moteur/js/assiette.js`, `moteur/js/cout.js`,
`moteur/js/macro.js`, `scripts/construire_donnees.py`, `tests/test_cout.py`,
`tests/test_donnees.py`, `limites.md` § 5 bis et § 5 ter,
`data/reference/prose/zones.yaml`.

---

### 66. Deux écarts de comptabilité : la convention qu'on ne disait pas, et le brut qu'on ne disait pas non plus — `fait`

**Demande.** « Fais les trois écarts qui restent », à la suite de l'audit de
l'action 65. Les deux premiers sont ici ; le troisième, les engagements acquis
à date, a sa propre entrée.

**La convention comptable, et pourquoi elle n'est pas un détail.** Le compte du
COR est tenu sous convention EPR : ce que l'État verse au régime de ses
fonctionnaires et aux régimes spéciaux y suit, année par année, ce qu'il faut
pour les équilibrer. Ces régimes ne montrent donc JAMAIS de déficit, et le
−2,4 points de PIB que le site affiche pour 2070 est le déficit de ce qui
RESTE, une fois la fonction publique bouclée. La mention était dans l'en-tête de
`comptes_retraite.csv` depuis que la série existe, et nulle part dans la prose :
un lecteur qui ne la connaît pas lit le chiffre pour ce qu'il n'est pas.

**Ce que l'autre convention donne, et le résultat qui surprend.** Le COR publie
aussi l'effort de l'État figé en part de PIB (EEC), en données complémentaires
de sa figure des ressources. On attend d'une hypothèse nommée « effort
constant » qu'elle soit sévère ; elle ne l'est pas, et pas non plus l'inverse :
**l'écart change de signe**. L'assiette de cotisation des trois fonctions
publiques recule de 10,4 % du PIB à 8,9 % — moins de fonctionnaires, et des
primes qui montent plus vite que le traitement indiciaire —, donc le besoin de
ces régimes recule aussi ; l'effort figé est SOUS le besoin tant qu'ils pèsent,
et au-dessus ensuite. EEC donne 0,67 point de moins en 2028, croise en 2047, et
rend 0,49 point de plus en 2069. Sur 2026-2069 les deux moyennes ne diffèrent
pas de deux centièmes de point. Aucune ne flatte : l'une creuse le déficit de
demain, l'autre celui d'après-demain.

**Ce qu'il a fallu écrire pour l'obtenir.** `_annees_en_tete` s'arrête au
premier bloc d'une feuille, et c'est voulu — c'est celui que la figure trace.
`lire_bloc_eec` lit le second, et rend les QUATRE variantes de productivité
sous leur étiquette ; choisir celle du scénario de référence est le travail de
`verifier_donnees.py`, qui la lit dans `hypotheses_projection.yaml`. Un
récupérateur qui trancherait figerait un scénario dans une couche qui ne le
connaît pas. La série entre tout entière au niveau `projetee`, y compris ses
deux premières années : le bloc commence en 2024 et n'y écrit pas les valeurs
observées, parce que sous EEC l'État ne verse pas ce qu'il a versé.

**Le brut, et une recette qui sort de la dépense.** Les pensions du compte sont
celles qui sont versées, avant CSG, CRDS et CASA : 13,68 % du PIB en 2024 en
brut, **au plus 12,43 % en net**. Et l'article L. 131-8, 3° e affecte 2,94 des
8,30 points de CSG d'une pension à la branche vieillesse : **un tiers de ce
qu'une pension paie revient au système qui la verse**, soit au plus 11,8 Md€ en
2024, le cinquième des impôts et taxes affectés qu'il encaisse. Le COR ne se
trompe pas en portant les deux flux, un compte d'encaissements le doit ; mais
qui lit ses deux colonnes comme deux grandeurs indépendantes se trompe de cette
somme. Les scénarios notionnels, eux, retirent les impôts affectés en entier :
la circularité disparaît avec, et ce n'est pas un hasard — un compte notionnel
ne crédite que ce qui est assis sur un revenu d'activité.

**Les deux chiffres sont des BORNES, et il faut le dire ainsi.** Le taux plein
est appliqué à toute la masse, alors que L. 136-8 exonère les petites pensions
et en soumet d'autres à un taux réduit. Les chiffrer juste demanderait la
distribution des pensions croisée avec le revenu fiscal des foyers : la DREES
publie la première, personne ne publie le croisement.

**Ce que la page dit maintenant.** Le dépliant « D'où viennent ces chiffres »
porte trois paragraphes de plus : la convention et les deux soldes, le brut et
le net, la recette circulaire. L'année de croisement des deux conventions est
CALCULÉE et non écrite — l'écrire en dur, c'était promettre le rapport de 2026.
Trois entrées du catalogue des affirmations et deux contrôles tiennent les
nombres ; `csg_affectee_vieillesse` est la seule donnée de droit ajoutée, elle
ne sert à aucun calcul de pension, et le `journal` de `veille.yaml` porte sa
ligne.

**Fichiers.** `scripts/fetch/cor_comptes_retraite.py` (`lire_bloc_eec`),
`scripts/verifier_donnees.py`, `data/reference/macro/ressources_eec_retraite.csv`,
`data/reference/legislation/prelevements_remuneration.yaml`,
`data/reference/legislation/veille.yaml`, `remuneration.py`,
`donnees/equilibre.py`, `web/pages.py`, `moteur/js/equilibre.js`,
`moteur/js/remuneration.js`, `moteur/js/pages.js`,
`scripts/construire_donnees.py`, `data/reference/site/affirmations.yaml`,
`tests/test_affirmations.py`, `tests/test_donnees.py`, `limites.md` § 5 bis.

---

### 67. Le stock : le dépôt ne montrait que des flux — `fait`

**Demande.** Le troisième des écarts de comptabilité de l'audit de l'action 65.

**Ce qui manquait, et pourquoi c'était le comble.** Tout ce que le site montre
du système de retraite est un FLUX : ce qui rentre et ce qui sort dans l'année.
C'est la moitié d'un compte. L'autre est ce que le système DOIT DÉJÀ, au titre
des droits que les vivants ont acquis — et elle n'était nulle part, alors que le
modèle est en comptes notionnels, où ce stock est par définition la somme des
capitaux virtuels.

**Ce qui est publié, et que personne ne cite.** Le règlement (UE) n° 549/2013
fait transmettre, tous les trois ans, un tableau supplémentaire sur les
retraites. Poste `F63_LE`, droits à pension dans le bilan de clôture. Pour la
France : **368 % du PIB en 2015, 431 % en 2018, 397 % en 2021**, presque
intégralement par répartition. `eurostat_engagements_retraite.py` va les
chercher, `engagements_retraite.csv` les porte, et la page Coût les affiche à
côté de ses flux.

**Ce qu'on en retient.** L'ordre de grandeur, et rien de plus : près de quatre
années de production d'engagement contre quatorze pour-cent de PIB de dépense
annuelle, soit une trentaine de fois le flux d'une année. C'est ce qui rend
absurde, dans les deux sens, l'idée qu'un tel système se solde comme un budget
annuel.

**Et l'écart entre transmissions est la seconde information.** Soixante-trois
points de PIB en trois ans, puis trente-quatre dans l'autre sens. Ce ne sont pas
des droits qui apparaissent et disparaissent : un droit acquis à date est une
somme ACTUALISÉE, et son niveau dépend d'un taux qui bouge d'un exercice à
l'autre bien plus que les droits eux-mêmes. C'est la raison pour laquelle ce
tableau est publié à part des comptes principaux, et pourquoi le dépôt le porte
comme un ordre de grandeur et jamais comme une dette. La page le dit.

**Les années sont LUES, pas reconduites.** `SerieAnnuelle` prolonge la valeur du
bord, ce qui n'aurait ici aucun sens : le producteur n'a rien transmis pour
2024, et dater de 2024 un engagement de 2021 serait une faute.
`annees_engagements` lit donc la FIABILITÉ, et un contrôle exige que les années
rendues soient espacées de trois ans exactement.

**Ce qui reste ouvert, et c'est le vrai chantier.** Le dépôt ne calcule pas le
SIEN. Un scénario notionnel produit nativement la moitié de la grandeur — le
capital virtuel des actifs en est la définition —, mais pas celle des retraités,
dont le capital a été converti en rente à la liquidation. Les additionner
demanderait de refaire ce que fait le tableau 29 : table de mortalité, taux
d'actualisation, hypothèses de revalorisation. Le modèle en a les moyens
techniques — `moteur/compte.py` calcule le capital notionnel année par année,
`cout.py` sait pondérer une grandeur de la grille par les effectifs de l'INSEE —
et ce qui manque est une DÉCISION : le taux d'actualisation, qui n'est pas un
calcul. Le résultat en dépendrait autant que celui d'Eurostat en dépend, et
serait donc un troisième chiffre conventionnel à côté de deux qui le sont déjà.
C'est la raison de ne pas l'avoir fait à la hâte, et non une raison de ne
jamais le faire : un compte notionnel qui ne sait pas dire ce qu'il doit est
un compte incomplet.

**Et ce n'est pas la dette que la page montre déjà.** `Dette` accumule les
soldes À VENIR avec leurs intérêts, à partir de zéro. Les droits acquis à date
sont ce qui est dû AUJOURD'HUI pour le passé. Deux questions, deux grandeurs,
et les additionner n'aurait aucun sens.

**Fichiers.** `scripts/fetch/eurostat_engagements_retraite.py`,
`scripts/verifier_donnees.py`, `data/reference/macro/engagements_retraite.csv`,
`data/sources.yaml`, `donnees/equilibre.py`, `web/pages.py`,
`moteur/js/equilibre.js`, `moteur/js/pages.js`, `scripts/construire_donnees.py`,
`data/reference/site/affirmations.yaml`, `tests/test_affirmations.py`,
`tests/test_donnees.py`, `limites.md` § 5 bis, `methodologie.md`.

---

### 68. L'engagement acquis du dépôt, sous le taux d'actualisation du COR — `fait`

**Demande.** « Calcule le nôtre, avec le taux d'actualisation du COR. » Faisait
suite à l'action 67, qui avait fait entrer l'engagement publié sans produire
celui du modèle, faute d'un taux d'actualisation — que l'action tenait pour une
décision et non un calcul.

**Le taux n'avait pas à être décidé : le COR en publie un.** La note de sa
figure du solde moyen à divers horizons, celle que le décret n° 2014-654
relatif au Comité de suivi des retraites encadre, dit que « le taux
d'actualisation est supposé égal chaque année à la croissance annuelle du
PIB ». C'est une LECTURE, pas une convention du dépôt, et elle change la nature
du problème.

**Parce qu'actualiser au rythme du PIB revient à sommer des parts de PIB.** Le
facteur d'actualisation et le dénominateur se simplifient exactement :
l'unité de tout le dépôt portait déjà l'actualisation. L'engagement est donc la
somme, année par année, de ce que les droits acquis feront verser, chacun
rapporté au PIB de son année — et il n'y a aucune convention de plus à poser.
C'est pourquoi l'action 67 le croyait hors de portée et ne l'était pas.

**Ce que le modèle trouve**, à 2021, dernière date qu'Eurostat transmette :
**579 % du PIB** pour le système actuel — 231 points de retraités, dont la
pension entière est un droit acquis, et 347 points d'actifs au prorata de leur
carrière faite. La proposition en doit **370 %**, le notionnel sur la seule part
salariale **162 %** : ces systèmes promettent moins, donc ils doivent moins.

**Et l'écart avec les 397 % publiés est un TAUX, pas un droit.** Les mêmes
droits, actualisés **deux points de plus par an**, valent exactement le chiffre
d'Eurostat. C'est la même démonstration que les soixante points d'écart entre
deux transmissions, faite cette fois de l'intérieur : un engagement acquis n'a
pas de niveau propre, il a un taux. La page affiche les deux et ne choisit pas,
et la grille de sensibilité est figée avec le reste pour que le lecteur voie la
pente.

**Trois conventions, toutes nommées.** Le PRORATA TEMPORIS pour ce qu'un actif
a acquis : celle du tableau 29 pour les régimes à prestations définies, et
surtout UNE convention appliquée aux six systèmes, sans quoi leurs engagements
ne se compareraient pas. Un compte notionnel donnerait la sienne sans
approximation — le capital virtuel EST le droit acquis — mais elle ne vaudrait
que pour cinq des six, et l'étalon serait hors du tableau. L'EXTRAPOLATION
au-delà de 2070, où l'INSEE cesse de projeter la pyramide : les cohortes déjà
nées y sont prolongées par la table de mortalité unisexe du dépôt, celle-là
même qui sert de diviseur aux comptes notionnels. Elle ne porte que 35 points
sur 579, et un test borne cette part — un résultat qui dirait d'abord une table
de mortalité ne vaudrait rien. Et le FIGEAGE sous les réglages de référence,
comme le reste du bilan : quatre-vingts années de flux ne se somment pas chez
le lecteur.

**Deux bugs trouvés en route, et il faut les dire.** `Population.effectif`
RECOPIE la pyramide de 2070 au-delà : demander l'effectif des 85 ans en 2085 y
rend celui des 85 ans de 2070, qui sont d'une tout autre cohorte. C'est ce qui
rend l'extrapolation par la survie nécessaire, et non facultative. Et la
première version prenait pour frontière la dernière année du PIB (2025) au lieu
de celle de la pyramide (2070), ce qui faisait passer quarante-cinq ans
d'effectifs par la table de mortalité : l'engagement tombait à 478 % et la part
extrapolée dépassait le total, ce qui l'a signalé.

**Ce qui reste.** L'engagement hérite de tout ce que la trajectoire suppose —
treize carrières, une grille au pas de cinq ans, une dépense projetée plus haute
que celle du COR (§ 5 ter). Il ne remplace pas le tableau 29 : il dit ce que le
modèle doit, sous une convention nommée, et ce que cette convention vaut.

**Fichiers.** `cout.py` (`calculer_engagements`, `EngagementAcquis`),
`donnees/bilan.py` (`EngagementFige`), `moteur/js/bilan.js`,
`scripts/construire_donnees.py`, `web/pages.py`, `moteur/js/pages.js`,
`data/derive/equilibre.json`, `data/reference/site/affirmations.yaml`,
`tests/test_affirmations.py`, `limites.md` § 5 bis.

---

### 69. La pyramide des âges refuse l'année qu'elle n'a pas — `fait`

**Demande.** « Corrige le piège dans `Population.effectif` », relevé en écrivant
l'action 68.

**Ce qu'il était.** `_annee_bornee` ramenait toute année dans la plage publiée,
des deux côtés. En deçà de 1962, c'est une approximation assumée et documentée :
la dépense observée commence en 1959, et ces trois années empruntent la pyramide
de 1962, dont la dépense pèse un demi pour cent de celle d'aujourd'hui. Au-delà
de 2070, c'était un piège, et personne ne s'y était encore pris parce que rien
n'y allait.

**Pourquoi emprunter au-delà n'est pas la même chose qu'emprunter en deçà.** Une
pyramide s'indexe par ÂGE. Rendre l'effectif des 85 ans de 2070 sous le nom des
85 ans de 2085, ce n'est pas décaler une population de quinze ans : c'est rendre
des gens nés quinze ans plus tôt, et morts. Reconduire la valeur de bord d'une
série annuelle, ce que fait `SerieAnnuelle`, ne change qu'un niveau ; reconduire
un âge change de cohorte.

**Ce qui rend le refus nécessaire, c'est que le chiffre emprunté est
PLAUSIBLE.** Il a le bon ordre de grandeur, il ne saute pas, rien ne le signale.
Le 20 septembre 2026 il a fait tomber l'engagement acquis du dépôt de 579 à
478 % du PIB, et ce qui l'a trahi n'est pas le chiffre : c'est une incohérence
interne du calcul, la part extrapolée dépassant le total. Un défaut qui ne se
voit qu'à ce prix-là doit refuser, et non emprunter.

**Ce qui est fait.** `_annee_bornee` emprunte toujours en deçà et lève au-delà,
des deux côtés du portage, avec un message qui nomme le remède :
`cout._courbes_survie`, qui prolonge une cohorte déjà née par sa propre survie.
`effectif_tranche` refuse aussi, tranche VIDE comprise — déléguer le refus aux
âges l'aurait laissée passer. Aucun appelant n'était concerné : tous bornent à
`HORIZON`, qui est par définition la dernière année que l'INSEE projette.

**Deux tests, dont un qu'aucun témoin n'atteignait.** Côté Python, l'emprunt en
deçà et le refus au-delà. Côté JavaScript, le même, dans `tests/js/moteur.test.js` :
rien dans le site ne demande la pyramide au-delà de 2070, donc les témoins de
pages ne peuvent pas couvrir ce chemin, et un portage qui emprunterait
rendrait des chiffres plausibles sous le nom d'une cohorte qui n'est pas la
leur.

**Fichiers.** `donnees/population.py`, `moteur/js/population.js`, `cout.py`
(docstring de `_courbes_survie`), `tests/test_cout.py`, `tests/js/moteur.test.js`.

---

### 70. Une année non mesurée ne se dit plus certifiée — `fait`

**Demande.** « Cherche d'autres pièges du même genre dans le dépôt », après
l'action 69. Le motif cherché : une valeur hors domaine, PLAUSIBLE, que rien ne
signale, et dont la reconduction change l'identité de ce qu'on lit.

**Ce que la recherche a passé en revue, et écarté.** Les clamps d'année de
`equilibre.recette_non_acquise` et de `carriere` : déclarés, et à part
constante. Le clamp d'âge de `vie_en_couple` : déclaré, et la table est
complète sur sa plage — aucun triplet manquant qui rendrait zéro en silence.
`valeur_par_generation` : rend `None` en deçà de la première génération, ce qui
est honnête, et reconduit au-delà, ce qui est la convention du droit constant.
Les six mémoires de fichiers : toutes indexées sur `st_mtime_ns` et la taille,
donc insensibles à deux écritures dans la même seconde. Et le portage
JavaScript de `SerieAnnuelle` reproduit exactement les branches du Python, y
compris celle qui était en cause.

**Ce qu'elle a trouvé.** `SerieAnnuelle` porte, deux lignes sous le commentaire
qui écrit « une valeur interpolée n'est jamais *certifiée* », une branche qui
rend la fiabilité de l'année précédente telle quelle. Pour un BARÈME c'est
juste : l'année absente n'a pas changé, et la valeur de 2016 sous un seuil fixé
en 2015 est aussi certifiée que lui, parce que c'est la loi qui le dit. Pour
une ENQUÊTE, non : l'année absente n'a pas été MESURÉE.

**Le cas réel.** La DREES dénombre les retraités caisse par caisse et ne publie
pas la coordination RATP en 2022 — 2020, 2021, 2023, 2024, et rien entre les
deux. Vérifié chez le producteur, le trou est réel et non un défaut de
récupération. Le dépôt rendait **3 672 retraités en 2022, marqués `certifiee`**,
c'est-à-dire « recontrôlés contre le fichier de l'institution qui les
produit » — alors qu'il n'y a pas de fichier. Même chose, latente, dans
`droits_derives.csv`, où seule une caisse non lue porte le trou.

**Ce que le dépôt disait déjà, et que la branche démentait.** Hors de la
fenêtre 2004-2024, la répartition du bord est reconduite « et la série tombe au
niveau `estimee` pour le dire ». À l'intérieur, un trou gardait `certifiee` :
la règle était écrite, et son exception ne l'était pas.

**Le remède est un troisième mode d'interpolation, `ponctuelle`.** Il répond à
la seule question qui compte — que veut dire une année absente ? `escalier`,
elle n'a pas changé ; `lineaire`, la grandeur est continue et on interpole ;
`ponctuelle`, elle n'a pas été mesurée, et la valeur du bord est reconduite
comme dans l'escalier MAIS tombe à `estimee`. **La valeur ne change pas** : un
effectif reconduit reste l'estimation raisonnable qu'il était. Ce qui change est
qu'il se dit estimé, et la fiabilité se propage jusqu'au résultat affiché.

**Le second piège, structurel.** Treize séries sont déclarées DEUX FOIS — une
fois par le modèle, une fois par `construire_donnees.py` pour le paquet — et le
paquet porte l'interpolation que le navigateur applique. Deux déclarations qui
divergeraient feraient dire deux choses aux deux portages sur une année
absente, et **aucun témoin ne le verrait** : le site n'affiche aucune de ces
années-là. Les treize s'accordent aujourd'hui ; un test les apparie désormais
par leurs VALEURS — un nom peut différer d'un côté à l'autre, une série
d'années et de valeurs identiques ne trompe pas.

**Une piste annoncée, et elle était fausse des deux côtés.** L'action avait
laissé ouvert ceci : « `structure_financement.csv` et `cotisants.csv` portent
les projections du COR par jalons, lues en escalier : 2029 y prend la valeur de
2023 ». Vérification faite, le 20 septembre 2026 :

- **`cotisants.csv` n'a AUCUN trou.** Elle est annuelle et complète, 2010 à
  2070, pour toutes ses caisses. Elle avait été écartée de l'affichage du
  balayage par un filtre, puis nommée sans être regardée.
- **`structure_financement.csv` en a — 155 clés à six jalons — mais ne passe
  pas par `SerieAnnuelle`.** `StructureFinancement` a son propre lecteur, qui
  **REFUSE** une année non publiée : « Interpoler une structure de financement
  entre 2030 et 2040 reviendrait à inventer une trajectoire que personne n'a
  calculée. » Demander 2029 y lève une `KeyError` qui nomme les années
  disponibles.

Il n'y a donc rien à trancher, et surtout : **le dépôt portait déjà le remède
de l'action 69**, dans ce module, et depuis plus longtemps. C'est là qu'est le
motif de référence pour une grandeur dont une année absente n'a pas de sens —
refuser en nommant ce qui existe —, et `donnees/population.py` y renvoie
désormais.

La leçon est celle de tout ce lot, et elle vaut contre son auteur : une
affirmation plausible qu'on n'a pas éprouvée est du même bois que la valeur
plausible qu'aucun test ne regarde. Les autres conclusions du balayage, elles,
avaient été sondées — la table `vie_en_couple` comptée triplet par triplet, les
six signatures de mémoire lues une à une, les treize déclarations appariées par
un test qui tourne.

**Fichiers.** `donnees/chargement.py`, `moteur/js/serie.js`,
`donnees/effectifs.py`, `donnees/depenses.py`, `donnees/equilibre.py`,
`scripts/construire_donnees.py`, `scripts/verifier_donnees.py`,
`data/reference/regimes/effectifs_retraites.csv`, `tests/test_donnees.py`,
`tests/js/moteur.test.js`.

### 71. « Dont » là où il fallait lire « en plus » : la garantie vieillesse manquait au total de la proposition — `fait`

**Demande.** « Est-ce qu'on peut voir les dépenses et les recettes du scénario
parti libéral français ? J'ai l'impression que ce qui est affiché dans la page
coûts ne représente pas les vrais chiffres. » L'impression était juste, et pour
une raison qui tient en un mot.

**Ce que le modèle fait, et qui est juste.** La garantie vieillesse a quitté la
masse contributive du scénario 6 le 19 septembre 2026 : elle est financée par
l'impôt, et la compter dans la dépense d'un système qui ne l'encaisse pas
l'aurait fait payer deux fois. `masse_du_scenario` ne la porte donc pas, et
`postes_depenses` le dit — « elle n'entre pas dans `depense` ». Rien à changer
de ce côté.

**Ce que la page en disait, et qui ne l'était pas.** Les deux tableaux des
quatre systèmes portaient la composante sous l'étiquette « **dont** garantie
vieillesse du système 4 ». Un « dont » annonce une part d'un total qui la
contient ; celui-là désignait une somme qui s'y AJOUTE. La preuve était sous
les yeux du lecteur et personne ne l'avait lue : sur le passé observé, les
systèmes 3 et 4 affichaient le même 7 046 Md € au centime près — or seule la
garantie les sépare avant la bascule. Un « dont » de 1 930 Md € ne peut pas
sortir de deux totaux identiques dont l'un n'a pas de garantie. Le dépliant de
la cascade, lui, disait juste depuis toujours : « il s'AJOUTE à la dépense »,
et arrivait à 283,0 Md € en 2025 quand la carte de tête en montrait 261,4.

**Ce qui est fait.** Les deux lignes s'appellent « s'ajoute au système 4 », et
les deux tableaux portent désormais le TOTAL — 8 977 Md € cumulés sur
1959-2024 et 281,7 Md € en 2024 ; 381 Md € en 2070 et 16 656 Md € cumulés,
garantie nette des reprises comprise. La courbe de tête porte sa glose, « hors
garantie vieillesse », et le solde de la carte dit la même chose en trois mots.
Le tableau poste par poste n'avait pas à changer : sa ligne « pour mémoire,
hors du compte » était exacte.

**Trois autres écarts, trouvés au passage sur les RECETTES.** Le dépliant des
transferts additionnait trois payeurs et n'en nommait que deux : il écrivait
que la branche famille et l'assurance chômage expliquaient « 8,5 % des
ressources, sur les 4,8 % du poste transferts » — un sous-ensemble plus grand
que son ensemble. Les deux caisses en font 3,7 % ; les 4,8 % qui manquaient
sont ceux du fonds de solidarité vieillesse, dont la recette arrive par la CSG,
c'est-à-dire par le poste « impôts et taxes affectés » et non par les
transferts. Même omission dans la note qui suit — 10,9 + 3,9 milliards valent
0,50 % du PIB, et non les 1,17 % annoncés, qui comptent les 19,6 milliards du
fonds — et dans celle du coefficient d'équilibre. Le modèle, lui, retirait bien
les trois, et `retrait_par_impot` évitait déjà le double retrait : c'est la
prose qui nommait deux payeurs sur trois. Enfin, « le système de retraite y
prélève **aujourd'hui** 30,7 % » lisait `horizon.taux_prelevement`, qui est le
taux de 2070 ; celui de 2025 est 32,8 %. Les deux sont maintenant donnés, avec
leur année.

**Le contrôle qui manquait.** `garantie_hors_masse_contributive` tient
l'affirmation : sur le passé observé, la masse du scénario 6 est égale à celle
du scénario 4 au centime, et la garantie n'est pas nulle ; à l'horizon, le taux
unique les sépare dans l'autre sens, la garantie restant par-dessus. Trois
entrées du catalogue s'y accrochent.

**Ce que le premier passage avait laissé.** Quatre renvois de la page et des
docs nommaient encore la ligne « dont garantie », qui n'existe plus, et le
tableau « ce qui pousse la dépense » gardait la colonne de la proposition sans
sa garantie sans le dire — il le dit maintenant, et donne le total, 10,0 % du
PIB en 2070, 9,8 % net des reprises. Trois chiffres de `limites.md` avaient
aussi cessé de suivre la page : la garantie de 2024 y valait 19,5 milliards et
le surcoût pour l'impôt 11,7, quand la page calcule 20,7 et 12,9 ; et le
tableau des quatre lectures du barème donnait les coûts d'AVANT le recours d'un
ayant droit sur deux, adopté le 20 septembre — 18,4, 32,2, 30,0 et 53,7
milliards là où la page en affiche 9,2, 16,1, 15,9 et 28,5. Les deux dernières
lignes portaient en outre un facteur de déplacement périmé (0,64 pour 0,61), et
donc une part de retraités sous le plancher trop basse. Le tableau porte
désormais les deux populations — tous ceux qui sont sous le plancher, et ceux
qui réclament — pour qu'on ne puisse plus confondre les deux comptes.

**Fichiers.** `src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`data/reference/site/affirmations.yaml`, `tests/test_affirmations.py`,
`docs/limites.md`, `tests/temoins/pages.json`.

### 72. Le poids des deux sexes était celui d'une autre population que celle dont le coût est tiré — `fait`

**Demande.** « Tu es sûr que la garantie vieillesse a ce coût ? On a fait tout
un travail de recherche avec la différence homme/femme dans des commits
récents. Fouille bien et vérifie tout ça. »

**Le coût brut, lui, tient.** Il a été refait de bout en bout hors du modèle,
à partir du CSV de l'EIR seul, sans appeler aucune fonction du dépôt : 32,7 %
des retraités sous le plancher majoré aux pensions de 2020 et 57,0 milliards
d'euros de 2026 avant recours, 58,03 % et 28,5 milliards après recours aux
pensions du scénario 6. Ce sont les quatre nombres que la page affiche, au
dixième. `_manque_moyen` a été vérifié à la main sur une tranche pleine et sur
la tranche qui chevauche le plancher. Rien à reprendre de ce côté.

**Ce qui ne tenait pas est le POIDS DES DEUX SEXES.** L'action du 20 septembre
avait fait entrer le sexe dans le suivi des avances : les bénéficiaires sont
surtout des femmes, elles vivent plus longtemps, et leurs avances durent
d'autant. Pour peser les deux courbes de survie, il fallait la part des femmes
parmi les bénéficiaires, donc la part des femmes dans la population — et le
dépôt n'en avait pas : ni la pyramide des âges de l'INSEE, qui ignore la
retraite, ni les effectifs de la DREES, qui ignorent le sexe. Le modèle avait
donc pris ses courbes de survie à 65 ans et en avait tiré, en population
stationnaire, **56,0 %**.

**Ce poids était dans le fichier, et exactement.** L'EIR publie trois
colonnes — les femmes, les hommes, l'ensemble —, et la troisième est le mélange
des deux premières : il existe un poids, et un seul, tel que `w·F + (1−w)·H`
redonne l'ensemble tranche par tranche. Les quarante-six tranches de 2020 le
donnent toutes entre 0,52 et 0,53 — l'écart est celui de l'arrondi au centième
de point de la publication —, et les moindres carrés le fixent à **52,8 %**,
avec un résidu de 8·10⁻⁵.

**Et l'écart comptait, parce qu'il faisait parler de deux populations à la
fois.** À 56,0 %, recomposer les deux sexes donnait 58,99 % de retraités sous
le plancher majoré aux pensions du scénario 6 ; la colonne « ensemble » — celle
dont le coût est tiré — en donne 58,03 %. Le même calcul disait donc deux
choses de la même population, à un point près. Un poids sur les 65 ans et plus,
appliqué à des distributions de TOUS les retraités.

**Ce que le remède déplace.** La part des femmes parmi les bénéficiaires passe
de 68 à 66 %, la durée d'une avance de 20,5 à 20,4 ans, le nombre d'avances par
succession de 1,28 à 1,29, la couverture ne bouge pas (37 %), et le net de 2070
reste à 9,2 milliards. **Le coût brut ne bouge pas d'un centime** : il est lu
sur la colonne « ensemble », sans passer par le poids. C'était une
contradiction interne, pas une erreur de niveau — et c'est bien pour cela
qu'aucun chiffre affiché ne la trahissait.

**Le test qui manquait.** `test_les_deux_sexes_recomposent_la_colonne_dont_le
_cout_est_tire` refait le raccord : à ce poids-là, et à lui seul, le mélange
des deux colonnes de sexe redonne la colonne « ensemble », sur les parts de
chaque tranche et sur la part sous le plancher, aux pensions d'aujourd'hui
comme à celles du scénario 6. `donnees.distribution.part_femmes` refuse par
ailleurs un fichier dont les trois colonnes ne se répondraient plus.

**Ce qui a été vérifié et laissé tel quel.** Les quatre chiffres par sexe de la
page Programme (46 % des femmes contre 18 % des hommes sous le plancher
aujourd'hui, 72 % contre 42 % aux pensions du scénario 6) sont calculés colonne
par colonne et ne passent pas par le poids : ils sont justes. Le nombre
d'avances par succession est correctement pondéré PAR AVANCE et non par
succession — c'est bien ce que demande la boucle de couverture, qui parcourt
les avances. Et la réserve de fond n'a pas changé de sens : le déplacement de
la distribution est proportionnel et uniforme, alors que le scénario 6 retire
surtout des droits non contributifs que les femmes détiennent plus souvent ;
il fait donc tomber leurs pensions plus que la moyenne, et le coût affiché est
à ce titre une borne basse.

**Fichiers.** `src/retraite_notionnelle/donnees/distribution.py`,
`src/retraite_notionnelle/cout.py`, `moteur/js/distribution.js`,
`moteur/js/cout.js`, `tests/test_cout.py`, `docs/limites.md`,
`moteur/donnees.json`, `tests/temoins/pages.json`.

### 73. La réserve du déplacement uniforme cesse d'être une phrase : un milliard par quinze points d'écart — `fait`

**Demande.** « Vas-y », après l'action 72, qui se terminait sur la seule
réserve de fond restée non chiffrée : le déplacement de la distribution est
proportionnel et uniforme, alors que le scénario 6 retire surtout des droits
non contributifs que les femmes détiennent plus souvent. Leurs pensions
tombent donc plus que la moyenne, et le coût affiché est une borne basse. De
combien, personne ne le disait.

**Le chemin direct était fermé, et il fallait le constater avant de le
contourner.** Un facteur par sexe se tire de la grille de cas types comme le
facteur d'ensemble s'en tire — et **un seul des treize cas types est une
femme**. Une carrière ne fait pas une population, et un facteur féminin tiré
d'elle seule serait moins fiable que la convention qu'il prétendrait corriger.
Le dépôt ne porte par ailleurs aucune ventilation par sexe du coût des
avantages non contributifs, qui aurait été l'autre chemin ; ni
`data/reference/`, ni le module `avantages` ne la donnent.

**Ce qui restait possible, et qui est une mesure.** L'EIR publie les deux
sexes à part : on peut donc déplacer chaque distribution du sien. De combien
elles diffèrent est ce que personne ne publie — mais on n'est pas obligé de le
supposer, on peut le PARAMÉTRER, par le seul rapport `r = f_F/f_H`, et imposer
que la moyenne d'ensemble bouge du même facteur qu'aujourd'hui :

    w·μ_F·f_F + (1−w)·μ_H·f_H = f·(w·μ_F + (1−w)·μ_H)

`w` est la part des femmes dans l'enquête, 52,8 %, celle que l'action 72 a
établie ; `μ_F` et `μ_H` valent 1 120 € et 1 749 € en 2020. **La contrainte est
ce qui fait de l'exercice une répartition et non une hypothèse de plus** : la
grille garde le dernier mot sur l'agrégat, et le calcul ne décide que du
partage entre les deux sexes.

**Le résultat, au plancher majoré et à l'année de l'enquête.**

| `r` | f_F | f_H | sous le plancher | coût | écart |
|---|---|---|---|---|---|
| 1,00 *(convention)* | 0,606 | 0,606 | 58,03 % | 28,5 Md € | réf. |
| 0,95 | 0,588 | 0,619 | 58,04 % | 28,9 Md € | +0,3 |
| 0,90 | 0,569 | 0,633 | 58,07 % | 29,3 Md € | +0,7 |
| 0,85 | 0,550 | 0,647 | 58,19 % | 29,7 Md € | +1,2 |
| 0,80 | 0,529 | 0,662 | 58,37 % | 30,3 Md € | +1,8 |

Au plancher de base : 15,9, 16,2, 16,6, 16,9 et 17,4 milliards.

**Ce que cela établit.** Le SENS — le coût ne baisse jamais, quel que soit
`r`, parce que déplacer davantage les pensions les plus basses fait passer
plus de monde sous le plancher — et l'ORDRE DE GRANDEUR : **environ un
milliard par quinze points d'écart, moins de 5 % du total au bout de la
fourchette**. La réserve est réelle, son sens connu, sa taille seconde, et
elle ne renverse aucun chiffre de la page. Ce que cela n'établit pas est la
valeur de `r` : elle reste un paramètre, et se lit `r ≈ (1 − a_F)/(1 − a_H)`,
où `a_s` est la part non contributive de la pension du sexe `s` — un `r` de
0,90 dit que cette part dépasse d'environ dix points chez les femmes. La
mesurer demande une ventilation par sexe des avantages non contributifs, ou
une grille qui ne compte pas une femme sur treize.

**Où le calcul vit.** Dans `garantie.py` — `facteurs_par_sexe`,
`pension_moyenne`, `cout_garantie_par_sexe` — et non dans le script, parce que
la page en affiche deux lectures et qu'un nombre écrit en toutes lettres dans
sa prose serait démenti au premier réglage. Portage JavaScript fait, témoins
régénérés. `scripts/garantie_par_sexe.py` imprime le tableau entier ;
`tests/test_garantie_par_sexe.py` tient le raccord — à `r = 1`, le script
redonne le coût de la page, à l'arrondi de publication près et pas mieux, la
DREES arrondissant ses parts au centième de point. Un contrôle du catalogue,
`deplacement_uniforme_borne_basse`, tient les deux moitiés de la phrase que la
page affirme : jamais moins, et moins d'un dixième de plus.

**Fichiers.** `src/retraite_notionnelle/garantie.py`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/garantie.js`,
`moteur/js/pages.js`, `scripts/garantie_par_sexe.py`,
`tests/test_garantie_par_sexe.py`, `tests/test_affirmations.py`,
`data/reference/site/affirmations.yaml`, `docs/limites.md`,
`tests/temoins/pages.json`.

### 74. Le compte du COR est lu dans un seul scénario, et la croissance ne déplace qu'une moitié du bilan — `fait`

**Demande.** « Tu peux regarder si on n'a pas oublié des sources de recettes ?
En effet, avec la croissance à 1 %, on devrait avoir moins de chômage et plus
de recettes. » La question portait sur un poste manquant ; ce qui manque n'est
pas un poste.

**Aucune source de recette ne manque, et c'est tenu par un test.** Les six
postes de `equilibre.POSTES` sont la ventilation entière du COR —
`test_les_postes_couvrent_la_structure_des_ressources` exige que leurs parts
somment à un, année par année. Les trois que la proposition n'encaisse pas
sont chiffrés un par un par `scripts/postes_ecartes.py`. Ce qui reste dehors
est hors périmètre et déclaré : les réserves financières (un stock, quand le
solde est un flux), le RAFP, et les produits financiers que la convention EPR
écarte.

**Ce qui manque est la RÉACTION, et elle manque des deux côtés à la fois.**
Mesuré aux trois variantes de productivité du COR — 0,4 %, 0,7 %, 1,0 % — sur
la section « solde » de la page Coût :

| en % du PIB, 2070 | 0,4 % | 0,7 % | 1,0 % |
|---|---|---|---|
| ressources | 12,910 | 12,910 | 12,910 |
| dépense du système 1 | 15,300 | 15,300 | 15,300 |
| solde du système 6 | +0,419 | −0,139 | −0,724 |

Les deux premières lignes ne bougent pas d'un millième, ni entre les trois
scénarios, ni entre les deux trajectoires d'emploi : `comptes_retraite.csv` ne
porte que la colonne « Sc. Ref » du COR, et `ComptesRetraite` la lit quel que
soit le scénario demandé. La troisième bouge de 1,14 point.

**Sur les recettes, l'immobilité est JUSTE, et c'est la réponse à la question
posée.** Une croissance plus forte donne plus de recettes en euros, et la même
part de PIB : l'assiette et le PIB montent du même pas, et
`hypotheses_projection.yaml` s'interdit explicitement de déformer le partage de
la valeur ajoutée. Tout le bilan étant en part de PIB, une recette qui ne bouge
pas est ce qu'il faut attendre. Le raisonnement vaut aussi pour l'emploi :
rejouée sous `emploi=constant` au lieu de la trajectoire du COR, la recette de
2070 vaut 12,9105 % des deux côtés, et c'est exact — moins d'emploi, moins de
PIB, même rapport.

**Sur les dépenses, l'immobilité est FAUSSE, et le dépôt le démontre contre
lui-même.** La croissance travaille sur l'autre moitié du bilan : une pension
indexée sur les prix décroche d'un PIB qui accélère. La trajectoire de la page
Coût, elle, le mesure — c'est le modèle du dépôt, pas une série empruntée :

| en % du PIB, 2070 | 0,4 % | 0,7 % | 1,0 % |
|---|---|---|---|
| système 1, trajectoire du dépôt | 19,735 | 18,347 | 17,086 |
| système 6, trajectoire du dépôt | 9,540 | 9,537 | 9,536 |
| système 6, section « solde » | 7,840 | 8,432 | 9,051 |

La deuxième ligne est le comportement attendu d'un compte notionnel : des
droits indexés sur la masse salariale coûtent la même part de PIB quelle que
soit la croissance. La troisième est la même grandeur, calculée autrement —
`dépense du COR × rapport` —, et elle monte de 1,21 point sur la même
fourchette. Le rapport, lui, est bon (0,5124 → 0,5916 : le notionnel économise
moins quand la croissance est forte, puisque c'est le droit en vigueur qui
profite de l'indexation sur les prix) ; c'est le NIVEAU auquel on l'applique
qui est gelé sur 0,7 %. Un rapport qui monte à juste titre, multiplié par une
dépense qui devrait baisser et ne baisse pas : le produit compte deux fois dans
le même sens.

**Conséquence sur ce que le site affiche.** Le lecteur qui choisit la variante
haute voit la proposition perdre 0,58 point de PIB en 2070 et 0,45 en 2050,
sans qu'aucun mécanisme économique le justifie. C'est l'inverse du sens
attendu, et c'est un artefact de raccord.

**Le chômage ne se déduit pas de la productivité, et le COR ne le fait pas
non plus.** Ses variantes de productivité tiennent le chômage à 7 % — l'en-tête
de `emploi_projete.csv` nomme le scénario lu : « productivité 0,7 - chômage
7 % ». Le chômage est chez lui une DIMENSION SÉPARÉE, avec ses propres
variantes publiées (onglets `Chô_5%`, `Chô_7%`, `Chô_10%` de
`hypo_cotisants_chômage_2025.xlsx`, repérés sous l'action 27). Le dépôt n'en
porte aucune. Et quand bien même : en part de PIB, une variante de chômage
déplacerait la dépense, pas la recette, pour la raison ci-dessus.

**CE QUI A ÉTÉ FAIT, ET LA PREMIÈRE ÉTAPE A RENDU PLUS QUE PRÉVU.** La réserve
qui pouvait tout arrêter — le bloc EPR n'est peut-être pas publié par variante —
est levée : le COR le publie, dans des figures de SENSIBILITÉ que le dépôt ne
lisait pas. Le rapport de juin 2026 en porte six (2.18 à 2.23 : fécondité,
espérance de vie, solde migratoire, chômage, productivité, traitements
indiciaires), chacune republiant **la dépense et le solde du système** sous la
même note de bas de feuille que le compte principal — convention EPR, hors
produits et charges financières, ensemble des régimes légalement obligatoires,
FSV compris, hors RAFP. Deux sont prises : la 2.22 (productivité) et la 2.21
(**chômage**, que l'action n'espérait pas et qui est la question posée).

**La ressource est dérivée, et la dérivation est contrôlée avant d'être
utilisée.** Ces figures ne publient pas la ressource : elle est la somme de la
dépense et du solde. `source_comptes_variantes` confronte d'abord la ligne de
RÉFÉRENCE de chaque figure au compte principal, dépense contre dépense et somme
contre ressource ; elle le redonne à 5 × 10⁻⁷ près, c'est-à-dire à l'arrondi de
publication du classeur. Un écart plus grand arrête le script sans rien écrire :
il dirait que les deux figures ne sont pas du même exercice.

**Ce que ça a déplacé.** Le solde de la proposition en 2070, en points de PIB :

| | 0,4 % | 0,7 % | 1,0 % |
|---|---|---|---|
| avant | **+0,419** | −0,139 | **−0,724** |
| après | **+0,109** | −0,139 | **−0,336** |

L'amplitude tombe de 1,14 à 0,45 point, et le scénario de référence ne bouge
pas d'un centime — c'était déjà la colonne lue, et c'est le contrôle qui dit
que le raccord ne triche pas. Le résidu n'est pas un artefact : un compte
notionnel indexé sur la masse salariale est neutre à la croissance en part de
PIB, là où le droit en vigueur, indexé sur les prix, en profite. La proposition
gagne donc moins que le droit constant à ce que la croissance soit forte.

**Et la question de départ a sa réponse, qui n'est pas celle qu'on attendait.**
Moins de chômage donne **moins** de recettes en part de PIB — 12,86 % contre
12,91 % en 2070 sous la variante à 5 % —, et c'est la dépense qui recule, de
15,30 % à 15,02 %. En part de PIB, une assiette plus large ne rapporte pas
davantage : elle monte en même temps que son dénominateur. Le gain existe, il
est simplement de l'autre côté du compte.

**Ce qui reste ouvert, et c'est volontaire.** Le formulaire du site ne propose
que les trois scénarios de productivité : les deux variantes de chômage sont
dans les données et dans le compte, pas dans un bouton. Les ajouter demande un
champ de saisie, son portage et ses témoins, pour une dimension que le COR
traite à part ; `scripts/sensibilite_comptes.py` les imprime en attendant.
Restent aussi hors variante, faute que le COR les publie ailleurs que dans son
scénario de référence : le taux de prélèvement (figure 2.9), la structure des
ressources, les ressources EEC et les transferts. Les quatre réserves sont au
§ 5 de `limites.md`. Et quatre autres dimensions de sensibilité sont publiées
sans être lues — fécondité, espérance de vie, solde migratoire, traitements
indiciaires : le lecteur les prendrait sans une ligne de code nouvelle, il
manque seulement les scénarios correspondants dans `hypotheses_projection.yaml`.

**UN DÉFAUT QUE LES CHIFFRES NE MONTRAIENT PAS, ET QU'IL A FALLU REGARDER.**
Une fois les variantes branchées, les nombres étaient justes et la suite
verte. Le TRACÉ, non. L'axe de la carte du solde suivait ses données : 20 %
du PIB sous la référence, 15 % sous la variante haute. L'écart de 2070 perd
29 % de sa valeur entre les deux (2,39 point contre 1,69) et n'en perdait que
5 % de sa hauteur à l'écran — 37 pixels contre 35. Le lecteur qui bascule d'un
scénario à l'autre voyait une bande rouge presque inchangée alors que le
déficit avait fondu d'un quart. Ce n'est pas une régression de cette action :
l'axe s'adaptait déjà. Mais c'est elle qui rend ce graphique sensible au
scénario, donc elle qui transforme un comportement dormant en piège actif.
La carte porte maintenant le sommet de la variante la plus dépensière, commun
aux trois scénarios ; `gabarit.graphique` prend un `sommet_minimal` et
`depense_maximale_toutes_variantes` le LIT sur les variantes. Deux tests le
tiennent, dont un qui lit les graduations rendues plutôt que le paramètre :
ce qui doit tenir est ce que le lecteur voit. **La leçon vaut au-delà de cette
action : une suite verte ne dit rien d'un dessin.**

**Fichiers.** `scripts/fetch/cor_comptes_retraite.py` (`lire_sensibilite`,
`sensibilites`), `scripts/verifier_donnees.py` (`source_comptes_variantes`),
`data/reference/macro/comptes_retraite_variantes.csv` (nouveau, 360 valeurs),
`data/reference/macro/hypotheses_projection.yaml` (`variantes_chomage`),
`src/retraite_notionnelle/donnees/equilibre.py`,
`src/retraite_notionnelle/web/pages.py`,
`src/retraite_notionnelle/web/gabarit.py` (`sommet_minimal`),
`moteur/js/equilibre.js`, `moteur/js/gabarit.js`,
`moteur/js/pages.js`, `scripts/construire_donnees.py`,
`scripts/construire_temoins.py` (témoin `cout_variante_productivite`),
`scripts/sensibilite_comptes.py` (nouveau), `tests/test_cout.py`,
`tests/test_donnees.py`, `tests/test_affirmations.py`, `docs/limites.md`,
`docs/parcours_presentation.md`, `moteur/donnees.json`,
`tests/temoins/pages.json`.

### 75. `r` cesse d'être un paramètre : il est lu sur l'enquête, et il vaut 0,834 — `fait`

**Demande.** « Mesure `r` avec les avantages non contributifs par sexe »,
après l'action 73, qui l'avait laissé paramètre faute de source.

**Ce qui bloquait, et ce qui débloquait.** Un facteur par sexe se tire de la
grille comme le facteur d'ensemble s'en tire, et un seul des treize cas types
est une femme ; le dépôt ne portait par ailleurs aucune ventilation par sexe
du coût des avantages non contributifs. Mais l'échantillon interrégimes qui
porte la distribution porte AUSSI, dans un autre classeur du même millésime
(« Caractéristiques de tous les retraités », EIR 2020), les caractéristiques
des retraités par sexe. Elles n'étaient pas dans le dépôt : elles y sont.

**Les deux termes, et ils ne jouent pas dans le même sens.**

| | Femmes | Hommes | Rapport |
|---|---|---|---|
| Durée validée **non cotisée** | 26,0 % | 10,9 % | 0,740 / 0,891 = **0,831** |
| Majoration pour enfants, en part de la pension | 2,60 % | 3,04 % | 0,974 / 0,970 = **1,005** |
| | | | **r = 0,834** |

La durée non cotisée domine : un compte notionnel ne crédite que ce qui a été
cotisé, et une année validée sans cotisation n'y porte rien — AVPF, chômage,
maladie, majoration de durée. La majoration pour enfants, elle, joue à
L'ENVERS : dix pour cent de la pension pour trois enfants, c'est plus d'euros
à qui a la pension la plus haute. C'est exactement le terme qu'on aurait
supposé dans le mauvais sens.

**Trois contrôles croisés, tous passés.** La pension moyenne des femmes que le
dépôt calcule sur les tranches de la distribution — 1 120 € — contre 1 122 €
publiés : 0,14 % d'écart. Celle des hommes, 1 749 contre 1 784, soit 2,0 % de
moins, exactement ce que la tranche ouverte traitée en masse ponctuelle
retranche, et qui ne touche que les hommes (2,74 % d'entre eux au-delà de
4 500 € contre 0,24 % des femmes). Et surtout : **les effectifs publiés donnent
52,78 % de femmes**, là où l'action 72 avait ajusté 52,7758 % sur les trois
colonnes de la distribution. Le poids est désormais LU, et l'ajustement reste
comme vérification.

**Ce que la mesure déplace.** Le modèle applique `r = 0,834` au lieu de 1. La
garantie de 2024 passe de 20,7 à 22,0 milliards, celle de 2026 de 0,69 à
0,74 % du PIB, le versé de 2070 de 17,7 à 19,2, le cumulé 2026-2070 de 849 à
918. La part des femmes parmi les bénéficiaires monte de 66 à 70 %. Au barème
appliqué à la distribution, plancher majoré : 28,5 → 29,9 milliards. **La
convention uniforme sous-estimait de 5 %**, ce qui confirme l'ordre de grandeur
que l'action 73 avait annoncé sans la mesure.

**Le réglage garde les deux lectures.** `rapport_deplacement_sexe` vaut `None`
— lire l'enquête — et 1 restitue la convention d'avant, comme le dépôt le fait
partout où une décision remplace une convention.

**Ce que la mesure laisse dehors, et qui va dans le même sens.** L'enquête
publie la PART des bénéficiaires d'un minimum de pension — 46,5 % des femmes
contre 26,1 % des hommes — et non ce qu'il leur apporte : le retirer creuserait
l'écart. Le rapport suppose en outre le salaire porté au compte constant d'une
année cotisée à l'autre. `r = 0,834` est donc une borne haute, et le coût qui
en découle une borne basse — plus étroite qu'avant, dans le même sens.

**Fichiers.** `scripts/fetch/drees_caracteristiques_retraites.py`,
`data/reference/macro/caracteristiques_retraites.csv`, `data/sources.yaml`,
`scripts/verifier_donnees.py`,
`src/retraite_notionnelle/donnees/caracteristiques.py`,
`src/retraite_notionnelle/{config,cout,simulateur}.py`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/caracteristiques.js`,
`moteur/js/{config,cout,pages}.js`, `scripts/construire_donnees.py`,
`scripts/garantie_par_sexe.py`, `index.html`, `tests/`, `docs/limites.md`.

### 76. Ce que les minima apportent : mesuré, et laissé dehors pour une raison chiffrée — `fait`

**Demande.** « Mesure aussi ce que les minima apportent », après l'action 75,
qui avait laissé ce terme nommé faute que l'enquête publie autre chose que la
part de ses bénéficiaires.

**Une réserve qui se dissout par une lecture.** Le minimum vieillesse n'avait
rien à faire dans cette discussion, et il suffisait de regarder : l'enquête le
publie sur une ligne SÉPARÉE de la pension de droit direct, qui est l'assiette
de la distribution. Il n'est donc pas dans les pensions que le barème déplace.
Son chiffre par sexe est d'ailleurs instructif — 18 € par mois en moyenne chez
les hommes contre 13 chez les femmes, parce qu'ils tombent sous le plancher par
carrière très courte.

**Le minimum de pension, lui, est dedans, et il se chiffre en deux pièces.**
Les EFFECTIFS de bénéficiaires par sexe sont dans le classeur, feuille
« Minima », qui croise le sexe et le statut au regard du minimum : 4,33 millions
d'assurés au minimum de leur régime principal, dont **78 % de femmes**, et 6,10
millions tous régimes confondus, dont 67 %. Ils rejoignent la série certifiée.
La MASSE, en revanche, n'est publiée nulle part : elle est prise au modèle, qui
l'isole dans la cascade du scénario 1 — 2 912 millions en 2020.

**Le résultat.**

| Qui l'on compte | Bénéficiaires | dont femmes | Par mois | Part de la pension, F / H | × r |
|---|---|---|---|---|---|
| Au minimum de leur régime principal | 4,33 M | 78 % | 56 € | 1,92 % / 0,39 % | 0,985 |
| Tous régimes confondus | 6,10 M | 67 % | 40 € | 1,65 % / 0,58 % | 0,989 |

Le terme va dans le même sens que les deux autres et mènerait `r` de 0,834 à
0,821-0,825.

**Pourquoi il reste dehors, et c'est une décision chiffrée, pas un scrupule.**
Ce qu'il ferait au coût est **sous le pour cent** : 22,0 milliards de garantie
en 2024 deviennent 22,1 ou 22,2, et la part de PIB de 2026 ne bouge pas au
centième. Le retenir coûterait en revanche un couplage réel — la garantie
dépendrait du chiffrage des avantages, quatre secondes de calcul, pour un terme
dont le montant est pris au modèle là où les deux autres sont LUS sur la même
enquête au même millésime. La page l'affiche, le script l'imprime, un test le
tient ; `r` ne le porte pas.

**Une hypothèse, et une seule.** Que le minimum apporte autant à un
bénéficiaire qu'à un autre, quel que soit son sexe. L'enquête suggère que c'est
prudent : sur le minimum vieillesse, qu'elle chiffre, les hommes touchent
davantage.

**Fichiers.** `scripts/fetch/drees_caracteristiques_retraites.py`,
`data/reference/macro/caracteristiques_retraites.csv`,
`src/retraite_notionnelle/donnees/caracteristiques.py`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/caracteristiques.js`,
`moteur/js/pages.js`, `scripts/construire_donnees.py`,
`scripts/garantie_par_sexe.py`, `tests/test_garantie_par_sexe.py`,
`docs/limites.md`.

### 77. Le plancher d'une population n'est pas celui d'une personne : un quart de la garantie — `fait`

**Demande.** « Est-ce qu'il y a des choses à décider ? » — trois décisions
posées, et celle-ci tranchée : « 1. Corrige. »

**La convention qui restait, et c'était la plus grosse.** La trajectoire
servait le plancher MAJORÉ — 1 050 €, celui de qui vit seul — à la population
entière. Motif écrit sur la page : « l'enquête ne dit pas avec qui l'on vit ».
C'est vrai de l'enquête sur les pensions, et faux du dépôt : le recensement le
dit âge par âge et par sexe, `data/reference/macro/vie_en_couple.csv` le porte
depuis l'action 47, et `_reprises_successions` le LISAIT DÉJÀ pour compter les
avances par succession. La garantie le lit maintenant aussi.

**Ce que dit le recensement**, pesé sur les années vécues après 65 ans :
**61,8 % des femmes vivent seules contre 33,9 % des hommes**. Les deux
planchers se mélangent donc dans cette proportion, SEXE PAR SEXE — et pas
globalement, parce que les deux faits se composent : les femmes vivent seules
plus souvent et tombent sous le plancher plus souvent.

| | Garantie 2024 | 2026, % du PIB | Cumul 2026-2070 |
|---|---|---|---|
| Plancher majoré pour tous *(avant)* | 22,0 Md € | 0,74 % | 918 Md € |
| **Pesé par le recensement** | **17,8 Md €** | **0,59 %** | **745 Md €** |
| Plancher de base pour tous | 12,5 Md € | 0,42 % | 525 Md € |

**Près d'un quart de moins**, et c'est de loin la plus grosse correction de la
série — trente fois le terme des minima de l'action 76, cinq fois la mesure de
`r` de l'action 75. Ce n'était pas une prudence assumée : une borne haute faute
d'avoir cherché la source.

**Un bogue introduit et rattrapé dans le même tour**, qui mérite sa ligne. Le
raccourci de `chiffrer_distribution` — à rapport un, lire la colonne
« ensemble », seule lecture exacte — court-circuitait le mélange des planchers,
puisque cette colonne ne sait pas qui vit seul. Le test du script l'a attrapé
en une minute : sa colonne `r = 1` ne redonnait plus la trajectoire calculée
sous `rapport_deplacement_sexe = 1`. Le raccourci ne vaut désormais que s'il
n'y a RIEN à mélanger, ni rapport ni plancher.

**Ce qui ne change pas.** `situation_foyer` reste ce qu'il a toujours été pour
une CARRIÈRE : le simulateur demande la vôtre, et un individu a une situation.
Il ne décide simplement plus pour tous. Les deux planchers purs restent au
tableau des quatre lectures, où ils sont désormais nommés pour ce qu'ils sont —
les BORNES, pas le coût.

**Une réserve, et elle va dans le même sens.** L'exposition est pesée par la
table de la population générale et non par le vingtile des bénéficiaires ; les
plus modestes meurent plus tôt, donc pèsent moins les grands âges où l'on vit
seul, et la correction serait un peu plus forte avec leur table.

**Fichiers.** `src/retraite_notionnelle/garantie.py`,
`src/retraite_notionnelle/cout.py`, `src/retraite_notionnelle/web/pages.py`,
`moteur/js/garantie.js`, `moteur/js/cout.js`, `moteur/js/pages.js`,
`scripts/garantie_par_sexe.py`, `data/reference/site/affirmations.yaml`,
`tests/`, `docs/limites.md`, `tests/temoins/pages.json`.

### 78. Ce qui a changé de côté : la frontière contributive, datée et vérifiable — `fait`

**Demande.** « Plus de recherches sur tout ce qui n'est pas contributif dans les
retraites actuelles. Il y a sans doute des choses qui n'étaient pas
contributives avant et qui le sont devenues depuis ; et inversement. »

**Ce que l'inventaire ne pouvait pas dire.** `avantages_non_contributifs.yaml`
porte quarante-deux dispositifs avec une `creation` et une `fin`. Il décrit donc
une liste avec ses bornes, et rien entre les deux : un dispositif qui reste en
place et change de côté n'y laisse aucune trace. C'est exactement ce que la
demande visait, et la réponse n'était pas d'allonger l'inventaire mais de lui
ajouter une dimension.

**Le mot en cache trois, et elles bougent séparément.** « Non contributif »
désigne ce que l'assuré ACQUIERT sans cotiser, ce qu'il VERSE sans acquérir, et
QUI PAIE la charge. Le dépôt ne portait que la première ; la deuxième était
absente de bout en bout. La preuve que les trois sont distinctes tient en une
ligne : les indemnités journalières de maternité entrent au salaire de base en
novembre 2010 (L. 351-1), le fonds en prend la charge le même jour (L. 135-2
10°), et cette prise en charge est abrogée en décembre 2020 **sans que la
version de L. 351-1 bouge** — elle est toujours en vigueur. Un lecteur qui
mesurerait par les comptes verrait là une baisse qui n'existe pas.

**La liste existait, et c'est le législateur qui la tenait.** L'article L. 135-1
porte la seule définition légale de l'avantage « à caractère non contributif »,
et elle est énumérative : n'est non contributif que ce que L. 135-2 énumère.
Cette liste a été révisée **trente-sept fois de 1994 à 2025**. Chaque version est
une photographie datée de la frontière, prise par celui qui la déplace — et
elles sont toutes dans l'index LEGI du dépôt. L'appariement des points d'une
version à l'autre se fait par contenu et non par numéro : la renumérotation
complète de 2016 aurait sinon été lue comme neuf changements de fond.

**Elle disparaît le 1er janvier 2026, et cela coûtera une série.** L'article 24
de la LFSS 2025 abroge le chapitre du FSV — « les droits et obligations du Fonds
de solidarité vieillesse sont dévolus à la Caisse nationale d'assurance
vieillesse ». La liste survit sous L. 222-2-1, mais son 2° ne vise plus **le
régime général** : il a absorbé le fonds et ne se rembourse pas à lui-même. Le
coût des périodes assimilées du régime général cesse donc d'être un transfert
publié pour devenir une charge interne. C'est le plus gros contingent de la
ligne la plus lourde que le modèle calcule, et la série a désormais une date de
péremption.

**Le versant miroir, qui manquait.** Deux dates, lues dans L. 241-3 : les
cotisations vieillesse déplafonnées — qui n'ouvrent aucun droit, le salaire
au-delà du plafond n'entrant dans aucun calcul — sont à la charge de l'employeur
depuis le 20 janvier 1991, et du salarié depuis le 22 août 2003. Cela change la
lecture des scénarios : `config.py` porte au compte ce qui a été PRÉLEVÉ, taux
d'appel compris, donc les scénarios notionnels **rendent contributif ce que le
droit actuel stérilise**. Une part de l'écart qu'ils mesurent ne vient pas
d'avantages gratuits en plus, mais de cotisations rendues à leur cotisant. Ce
n'était nommé nulle part.

**Et un renversement, en 2023.** L'article L. 161-22-1-1 rend acquisitives les
cotisations du retraité qui reprend une activité, jusque-là à fonds perdus, et
définit au passage la seule pension purement contributive du droit français :
« seules sont retenues les périodes ayant donné lieu à cotisations à la charge
de l'assuré […] aucune majoration, aucun supplément ni aucun accessoire ne peut
être octroyé ». C'est l'objet que les scénarios 2 à 5 construisent par le
calcul, écrit par le législateur pour une pension et une seule.

**Ce qui tient le fichier.** Chaque bascule porte l'identifiant de la VERSION
d'article qui en fait foi, et `scripts/frontiere_contributive.py --verifier`
rouvre le dump LEGI pour confronter les quarante identifiants cités : le bon
article, la bonne date d'entrée en vigueur — ou de FIN quand c'est la
disparition d'une version qui fait l'événement, comme pour la cotisation
d'assurance veuvage, dont l'unique version court de 1985 à 2004. Le contrôle a
levé quatre écarts sur des lignes qui semblaient justes, et c'est lui qui a
imposé les trois raffinements du modèle de données : `preuve: fin`,
`date_preuve` — l'article 24 est en vigueur en mars 2025 et supprime le fonds en
janvier 2026 — et `article_precedent`, pour une comparaison qui traverse une
recodification.

**Une règle de classement, plus sévère qu'il n'y paraît.** Une bascule est
rangée sur la face que la version CITÉE prouve, non sur celle que son sujet
suggère. La validation des trimestres d'apprentissage est un droit gratuit ;
l'article lu ne dit que qui le paie, et la ligne est rangée en `financement`.
C'est ce qui empêche un inventaire de lectures de redevenir un inventaire de
souvenirs.

**Trois corrections à l'inventaire, au passage.** La pénibilité a un payeur
nommé depuis novembre 2010 — une contribution de la branche AT-MP inscrite à
L. 241-3 —, là où la ligne disait qu'aucun poste ne l'isolait : ce qui manque
n'est pas la charge, c'est sa publication. L'allocation veuvage a eu **sa propre
cotisation**, 0,10 % à la charge du seul salarié (D. 242-5), de 1985 à 2004 :
son invisibilité date du jour où elle a perdu son payeur nommé. Et le minimum
contributif a été rangé dans la solidarité par le législateur de décembre 2010 à
décembre 2016 — le seul cas où le modèle sait mieux que les comptes, la cascade
continuant d'isoler ce que la série publiée a cessé de dire.

**Ce que la chronologie montre.** Cinq ouvertures de droits gratuits contre une
fermeture qui n'en est pas une ; dix charges isolées chez un payeur nommé, dont
neuf avant 2015 ; cinq refondues dans les comptes, dont quatre depuis 2016. Le
mouvement des trente premières années a rendu la dépense lisible ; celui des dix
dernières la rend progressivement opaque. Et une bascule qu'aucun modèle
historique n'attend : le 9° de L. 351-3, entré en septembre 2023, valide
**rétroactivement** les travaux d'utilité collective des années 1980. Le droit
applicable à une année de carrière a changé quarante ans après cette année-là ;
le modèle date ses règles par l'année de la période et ne sait pas rejouer cela.

**Ce qui reste.** Le versant `cotisation` n'est pas chiffré : on sait depuis
quand la cotisation déplafonnée n'achète rien, pas combien elle pèse — il y
faudrait la distribution des salaires au-dessus du plafond. Le taux d'appel des
complémentaires relève du même chantier et n'est porté par aucune table. Les
bascules du code des pensions manquent, à commencer par la bonification pour
enfants restreinte aux naissances d'avant 2004. Et la liste légale n'a pas
encore été confrontée poste par poste à l'inventaire : c'est le chemin le plus
court vers ce qui manque aux quarante-deux dispositifs.

**Fichiers.** `data/reference/legislation/frontiere_contributive.yaml`,
`scripts/frontiere_contributive.py`, `tests/test_frontiere_contributive.py`,
`docs/frontiere_contributive.md`, `docs/avantages_non_contributifs.md`,
`data/reference/legislation/veille.yaml`, `data/reference/prose/zones.yaml`,
`data/sources.yaml`.
### 79. Le poids du recensement, mis en place jusqu'au bout — et une régression rattrapée — `fait`

**Demande.** « Met le poids du recensement en place », après l'action 77 qui
l'avait posé dans le coût mais laissé deux choses ouvertes.

**Ce qui manquait, et ce n'était pas une finition.** L'action 77 pesait les
deux planchers par le recensement, mais l'EXPOSITION — combien d'années on
passe à chaque âge — venait de la table de la population générale. Or qui vit
seul dépend de l'âge : les plus modestes meurent plus tôt, pèsent donc moins
les grands âges, ceux où l'on vit seul. Le recensement ne dit pas la même
chose selon la table qui le pèse : **61,8 % de femmes seules sous la table
générale contre 57,9 % sous celle du premier vingtile**, qui est celui des
bénéficiaires. Le vingtile est désormais calculé une fois, dans le calage, sur
la pension moyenne de ceux que le plancher majoré concerne.

**Une régression de l'action 77, trouvée en cherchant la première.** Cette
action-là avait fait de `plancher_mensuel` le plancher de BASE, le majoré
devenant un champ séparé. Or `_reprises_successions` lit `plancher_mensuel` —
et décrivait donc, depuis la veille, les seuls retraités sous 800 €, un
ensemble plus étroit, plus pauvre et plus féminin que celui que la garantie
sert. Aucun test ne l'a vue : elle ne déplaçait que des grandeurs que rien
n'épinglait.

| | Avant l'action 77 | Après (la régression) | Corrigé |
|---|---|---|---|
| Part des femmes parmi les bénéficiaires | 70,2 % | 75,6 % | **74,7 %** |
| Avances par succession | 1,270 | 1,181 | **1,212** |
| Couverture par les successions | 37,4 % | 41,4 % | **38,9 %** |

**Le remède est le même des deux côtés : décrire la même population.** Les
reprises portent désormais sur les QUATRE cas que la garantie sert — deux
sexes, deux planchers —, chacun sous son propre facteur de déplacement et son
propre plancher, pondérés par le recensement. Elles lisaient le bon facteur
depuis l'action 75 et le mauvais plancher depuis la 77 ; elles lisent
maintenant les deux. Le rang qui rattache une pension au patrimoine de son
quart reste celui de la distribution d'ensemble : le patrimoine n'est pas
publié par sexe.

**Ce que l'ensemble déplace**, par rapport à l'action 77 : la garantie de 2024
passe de 17,8 à **17,4 milliards**, celle de 2026 de 0,59 à **0,58 % du PIB**,
le cumulé de 745 à **729**. Par rapport à la convention d'avant le
21 septembre — le plancher majoré pour tous —, la correction totale vaut **plus
d'un cinquième** : 22,0 → 17,4 milliards.

**La leçon, et elle est la même que celle des actions 72 et 75.** Un calcul qui
décrit la même population deux fois de deux façons différentes finit toujours
par se démentir. Ici il l'a fait trois fois : le poids des sexes (action 72),
le facteur de déplacement (action 75), le plancher (celle-ci). À chaque fois le
remède a été de faire lire aux deux moitiés la même chose, et à chaque fois un
test l'a épinglé ensuite.

**Fichiers.** `src/retraite_notionnelle/cout.py`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/cout.js`,
`moteur/js/pages.js`, `scripts/garantie_par_sexe.py`, `tests/test_cout.py`,
`docs/limites.md`, `tests/temoins/pages.json`.

### 80. L'âge conjoncturel de la DREES, et le biais d'âge de la grille enfin mesuré — `fait`

**Pourquoi.** `docs/limites.md` § 5 ter portait depuis des semaines une
déduction non mesurée : les cas types entrant tard dans la vie active —
vingt-quatre ans pour l'artisan, vingt-sept pour le libéral — partiraient à
soixante-sept ans une fois la durée requise opposée, donc « la grille part, en
moyenne, un peu plus tard que la France réelle ». La section nommait elle-même
son instrument : « l'âge conjoncturel de départ que publie la DREES permettrait
de le chiffrer, et il n'est pas dans le dépôt ».

**Marche.** Le jeu est en open data, sur le portail que `drees_eacr.py` et
`drees_caracteristiques_retraites.py` interrogent déjà —
`scripts/fetch/drees_age_conjoncturel.py` le dépose, `verifier_donnees.py` le
certifie dans `data/reference/macro/age_conjoncturel_depart.csv` (dix-neuf
années, trois colonnes, cinquante-sept valeurs), et `scripts/age_conjoncturel.py`
fait la mesure : pour chaque année, l'âge auquel chaque cas type part —
interpolé entre les points de la grille, qui avance de cinq ans en cinq ans —,
les treize pesés par les effectifs de caisse de la page « Coût ».

**Ce que ça a déplacé.** La déduction était fausse, et c'est le résultat. **La
grille suit l'âge réel à moins d'une demi-année sur dix-neuf ans**, écart moyen
−0,08 an : elle part un peu plus TÔT, non plus tard. Aucun chiffre du site ne
bouge — la série ne nourrit aucun calcul, elle mesure la grille sans la
corriger —, et ce qui change est ce que le dépôt SAIT de sa propre grille : le
contrôle le plus large qu'il ait jamais eu sur la date de départ de ses cas
types, dix-neuf années au lieu d'une.

Le défaut que la mesure trouve n'est pas celui qu'on cherchait : il est dans la
PENTE. +0,26 an en 2010, −0,45 an en 2022 ; l'âge réel monte de 2,09 ans sur la
période, la grille de 2,00, et tout l'écart se creuse après 2015. La grille ne
connaît que ce que le droit ouvre, et la montée récente doit une part au
comportement, qu'aucun cas type ne choisit. C'est une piste pour la trajectoire
de 2070, pas une conclusion : une demi-année de départ ne referme pas quatre
points de PIB.

Trois leçons. **Une déduction écrite dans la prose reste une déduction**, même
bien raisonnée, même publiée depuis des mois : celle-ci se tenait, et la source
l'a démentie du premier coup. **Une source peut mesurer sans corriger**, et
c'est un usage légitime — cette série n'entre dans aucun calcul, et son intérêt
est entier. Et **le jeu est retrouvé par son titre, non par son identifiant** :
celui-ci porte le numéro de la figure dans l'édition du panorama
(« Graphique-1 »), qu'une édition suivante renumérotera.

**Ce qui reste.** La pondération est un STOCK de retraités, pas un flux de
liquidations — le dépôt n'a pas les seconds, et un régime dont les départs
ralentissent garde ici le poids de ses retraités d'hier. Le sexe n'est pas
comparé, la grille ne distinguant pas ses cas types. Et la DREES publie à côté
`departretraite_parcsp`, l'âge de départ par catégorie socioprofessionnelle :
c'est la comparaison cas type par cas type, celle qui dirait lequel des treize
part de travers, là où celle-ci ne juge que leur somme.

**Fichiers.** `scripts/fetch/drees_age_conjoncturel.py`,
`scripts/age_conjoncturel.py`, `tests/test_age_conjoncturel.py`,
`scripts/verifier_donnees.py`, `data/reference/macro/age_conjoncturel_depart.csv`,
`data/sources.yaml`, `docs/limites.md` § 5 ter.

### 81. Combien l'on cotise sans rien acquérir : 17,9 milliards, et une erreur corrigée — `fait`

**Demande.** Une recherche documentaire sur trois axes, dont le premier :
chiffrer les cotisations qui n'ouvrent aucun droit, et verser dans le dépôt ce
qui est certifiable.

**L'erreur d'abord, parce qu'elle était dans le dépôt.** L'action 78 avait
laissé écrit, au § 7 de `frontiere_contributive.md`, que le chiffrage butait sur
« la distribution des salaires au-dessus du plafond ». C'est faux. La cotisation
déplafonnée de L. 241-3 porte sur la TOTALITÉ de la rémunération, dès le premier
euro — l'assiette supra-plafond n'a rien à y faire, et la confusion valait un
facteur dix. Elle n'ouvre aucun droit pour autant : le salaire annuel de base
est borné au plafond par R. 351-29, les trimestres à quatre par an par R. 351-9.
Aucune distribution n'est donc nécessaire, et la masse est un simple produit.

**L'assiette vient de celui qui la recouvre.** Pas des comptes nationaux, qui
couvrent toute l'économie, fonction publique comprise — laquelle ne relève pas
de L. 241-3. L'Urssaf publie la bonne, et sa note méthodologique la DÉFINIT :
« la masse salariale correspond à l'assiette déplafonnée des cotisations
sociales ». Le portail était déclaré dans `sources.yaml` avec
`statut_integration: a_faire` depuis toujours ; il est désormais certifié,
vingt-neuf années de 1997 à 2025. L'écart avec les comptes nationaux n'est pas
une nuance : 726 Md€ contre environ 1 050 Md€ en 2024, soit 45 % de trop si
l'on prend l'une pour l'autre. Un test tient cet écart, parce qu'aucun autre ne
le verrait : mêmes colonnes, même unité, même allure de série.

**Le résultat : 17,9 Md€ en 2025**, dont 3,0 à la charge du salarié, pour le
seul régime général. Et il monte plus vite que l'assiette, le taux ayant été
relevé deux fois depuis 2023 — 2,42 % au 1er janvier 2024, 2,51 % au 1er janvier
2026.

**Un recoupement qui n'avait pas été cherché.** La part salariale du déplafonné
est nulle jusqu'en 2004 et positive à partir de 2005 dans la table certifiée,
construite depuis les DÉCRETS d'application. Or l'action 78 avait daté la
bascule du 22 août 2003, par la version de L. 241-3 qui ajoute « et des
salariés ». Les deux ne se contredisent pas : la loi autorise, le décret
exécute. Deux chemins indépendants se rejoignent à dix-huit mois près, et un
test tient désormais l'écart — il disparaîtrait sans bruit si quelqu'un alignait
l'une sur l'autre.

**La complémentaire est connue en proportion, pas en masse.** La fiche
réglementaire de l'Agirc-Arrco écrit que « seule » la cotisation au taux de
calcul des points est génératrice de droits, et que les deux contributions
d'équilibre de l'article 37 de l'ANI ne le sont pas. Sur la tranche 1, un
salarié verse 10,02 % et n'en acquiert que 6,20 : **38,1 % n'achète aucun
point**, 40,2 % s'il dépasse le plafond. Trois fois plus, en proportion, que le
régime de base. En faire une masse supposerait la répartition de l'assiette
entre tranches, que le dépôt n'a pas ; le rapport, lui, est exact.

**Le pourcentage d'appel a changé de signe**, et c'est le plus beau des trois
axes. Instauré en 1952 à l'Agirc, il était INFÉRIEUR à 100 % — 78 % en 1952,
95 % en 1965 — pour éviter de constituer des réserves : le cotisant versait
moins que le taux contractuel et acquérait les points du taux entier. Le même
instrument prélève aujourd'hui 27 % sans rien donner.

**Ce que le dépôt ne saura jamais certifier, et qui bouge quand même.** Les
régimes complémentaires vivent d'accords nationaux interprofessionnels, que le
Journal officiel ne publie pas : l'index LEGI ne les porte pas, et la sonde de
`--verifier` n'a rien à quoi les confronter. Les exclure aurait été absurde —
le taux d'appel est, en proportion, le prélèvement sans contrepartie le plus
lourd du système. D'où une section `bascules_hors_legi`, sous une preuve d'une
autre nature : une adresse et une date de lecture, que deux tests exigent.

**Ce que la recherche n'a pas donné, et il faut le dire.** Aucune masse de
cotisation sans droits n'est publiée par un producteur, ni à la DSS ni à
l'Agirc-Arrco : ils publient les taux et le mécanisme. Les 17,9 milliards sont
donc un calcul du dépôt sur deux séries publiées. Sur l'axe des bascules du code
des pensions, rien n'a été établi — ni la bonification pour enfants restreinte
aux naissances d'avant 2004, ni l'arrêt Griesmar, ni la fermeture des catégories
actives. Sur l'axe institutionnel, rien de postérieur au repère du COR de 2010
n'a pu être confirmé. Ces deux axes restent ouverts, et le § 7 de
`frontiere_contributive.md` les porte.

**Fichiers.** `scripts/fetch/urssaf_masse_salariale.py`,
`data/reference/macro/masse_salariale_privee.csv`, `scripts/verifier_donnees.py`,
`data/sources.yaml`, `data/reference/legislation/frontiere_contributive.yaml`,
`scripts/frontiere_contributive.py`, `tests/test_frontiere_contributive.py`,
`tests/test_donnees.py`, `docs/frontiere_contributive.md`,
`data/reference/legislation/veille.yaml`.
### 82. Lequel des treize part de travers : l'âge de départ par catégorie socioprofessionnelle — `fait`

**Pourquoi.** L'action 80 avait trouvé que la grille de cas types suivait
l'âge conjoncturel tous régimes à moins d'une demi-année sur dix-neuf ans, et
disait elle-même ce que ce résultat ne valait pas : une concordance d'ensemble
ne juge que la SOMME. Treize cas types dont l'un partirait deux ans trop tard
et l'autre deux ans trop tôt la donneraient tout aussi bien.

**Marche.** La DREES publie le même indicateur ventilé par catégorie
socioprofessionnelle, 2013 à 2020 : `scripts/fetch/drees_age_depart_csp.py` le
dépose, `verifier_donnees.py` l'écrit dans
`data/reference/macro/age_depart_csp.csv` au niveau `haute` — et non
`certifiee`, la source étant un sondage dont la DREES avertit qu'il est bruité
par catégorie. `data/reference/macro/cas_types_csp.yaml` écrit, cas type par
cas type, à quels groupes de la nomenclature il se compare et pourquoi ;
`scripts/age_depart_csp.py` fait la confrontation sur la moyenne pluriannuelle.

**Ce que ça a déplacé.** **Les écarts individuels valent 1,17 an, et ils se
compensent.** Pesés comme sur la page « Coût », les neuf cas types comparables
s'écartent de 1,17 an en valeur absolue et de +0,45 an seulement en signé, là
où le tous régimes donnait −0,10 an sur la même fenêtre. Un seul sur neuf tombe
dans son couloir. Le contractuel public sort de +2,34 an, l'artisan de +2,09,
le fonctionnaire sédentaire de +1,97 ; le salarié au SMIC de −1,59 et le chef
d'exploitation de −1,21.

Le sens des écarts désigne l'âge d'entrée, et c'est le mécanisme que
`limites.md` § 5 ter supposait : ceux qui partent le plus tard sont ceux dont
la fiche impose une entrée tardive — vingt-quatre ans pour le contractuel et
l'artisan, vingt-trois pour le cadre —, et qui doivent donc attendre la durée
requise ; le salarié au SMIC, entré à dix-huit ans, part à soixante ans tout du
long. Le mécanisme était bien là ; il ne se voyait pas parce qu'il se
compensait.

**Le couloir, et pourquoi ce n'est pas un point.** La nomenclature classe des
professions, la grille décrit des carrières par leur régime et leur niveau de
revenu. « Salarié au salaire moyen » ne dit pas si l'intéressé est technicien,
employé ou ouvrier : chaque cas type déclare donc TOUS les groupes où il peut
tomber, et l'écart est nul dès qu'il y tombe. Déclarer large affaiblit le
constat et ne le fausse jamais — le contractuel, qui réclame les quatre groupes
salariés, en sort quand même de plus de deux ans.

**Quatre cas types sont hors champ, avec leur motif écrit.** Le militaire,
l'agent de conduite, l'agent des IEG, le fonctionnaire de catégorie active :
leur départ n'est pas une sortie du marché du travail, et l'enquête Emploi
compte retraité qui se déclare tel. Une radiation à quarante-quatre ans suivie
d'un second emploi n'est pas l'événement que l'âge d'un groupe date. Ils pèsent
8,3 % de la grille et partent entre 44,0 et 56,6 ans — c'est aussi ce qui,
ajouté à la compensation, ramenait la somme à −0,10.

Trois leçons. **Une concordance d'ensemble ne vaut jamais comme un accord terme
à terme**, et le dépôt l'écrivait sans le vérifier : il a suffi d'un grain plus
fin pour que la réserve devienne un constat. **Le couloir est la bonne forme
quand la correspondance est incertaine** — il rend la déclaration large
inoffensive, et laisse le constat à sa charge. Et **le classement des
professions libérales compte** : la nomenclature les met dans le groupe 3 avec
les cadres, non dans le groupe 2 avec les artisans, et un test le tient parce
qu'on le suivrait mal de mémoire.

**Ce qui reste.** Aucun écart n'est corrigé : la mesure dit lequel des cas
types part de travers, elle ne réécrit aucune fiche — et le faire déplacerait
la trajectoire, ce qui est un chantier et non une retouche. La série s'arrête
en 2020, le jeu n'ayant pas été mis à jour depuis. Et la pondération reste un
stock de retraités, comme pour l'action 80.

**Fichiers.** `scripts/fetch/drees_age_depart_csp.py`,
`scripts/age_depart_csp.py`, `tests/test_age_depart_csp.py`,
`scripts/verifier_donnees.py`, `data/reference/macro/age_depart_csp.csv`,
`data/reference/macro/cas_types_csp.yaml`, `data/sources.yaml`,
`docs/limites.md` § 5 ter.

### 83. Ce que l'erreur d'âge coûte : rien, sur ce que le site compare — `fait`

**Pourquoi.** L'action 82 avait mesuré 1,17 an d'écart en valeur absolue entre
l'âge de départ des cas types et celui de leur catégorie socioprofessionnelle,
et le dépôt avait écrit qu'il ne corrigeait rien. Une erreur qu'on ne corrige
pas doit au moins être chiffrée : tant qu'on ne sait pas ce que ces 1,17 an
déplacent, on ne sait pas s'il faut réécrire une fiche ou fermer le sujet.

**Marche.** `scripts/cout_age_depart.py` fait le contrefactuel. Pour chacun des
neuf cas types comparables, il cherche l'âge d'entrée qui rapproche le plus son
départ du couloir de sa catégorie — l'âge d'entrée, parce que c'est la cause
que `limites.md` § 5 ter désigne, et parce que forcer l'âge de départ
directement donnerait une carrière que le droit ne produit pas. Puis il rebâtit
la grille avec ces âges et relance `cout.calculer_cout`. Six cas types se
déplacent : l'artisan entre à 21,5 ans au lieu de 24, le contractuel à 21 au
lieu de 24, le salarié au SMIC à 20 au lieu de 18.

**Ce que ça a déplacé.** **Les cinq scénarios notionnels ne bougent pas** —
moins d'un dixième de point de PIB en 2070, de −0,03 à +0,03. L'erreur d'âge
leur est invisible, et le mécanisme le dit : dans un compte notionnel, partir
plus tôt allonge le diviseur autant que la carrière raccourcie retire au
capital. C'est la raison chiffrée de ne réécrire aucune fiche pour ce que le
site argumente, et le sujet se ferme là.

**Le système actuel bouge, et dans le mauvais sens** : 18,35 % du PIB en 2070
sous les fiches, 18,95 % sous le contrefactuel, et l'écart avec la projection
du COR passe de 4,15 à 4,75 points. Corriger les âges ÉLOIGNE le modèle du COR.
L'âge de départ n'explique donc pas l'écart que le § 5 ter laisse ouvert, et la
piste qu'il nomme — un taux de remplacement qui ne recule pas quand celui du
COR recule — reste entière. Elle est la suite.

**Ce que la mesure laisse ouvert.** Sous la grille corrigée, l'écart à l'âge
conjoncturel tous régimes passe de −0,08 à −0,65 an : rapprocher chaque cas
type de SA catégorie éloigne leur SOMME. Les deux critères ne peuvent pas être
satisfaits ensemble. Le suspect est le groupe des quatre cas types hors champ —
un douzième de la grille, à des âges de 44,0 à 56,6 ans —, dont le poids ou
l'âge serait alors faux ; la mesure tient le constat et ne tranche pas son
explication, les deux sources ne décrivant pas la même population.

**Trois leçons.** **Un contrefactuel n'est pas une proposition** : aucun âge
d'entrée trouvé ici n'entre dans `castypes.py`, et un test l'exige — une fiche
se réécrit sur ce qu'on sait d'une carrière, pas sur ce qui rapproche une
moyenne d'une autre. **Le sens d'une correction se mesure avant de la faire** :
celle-ci allait dans le mauvais sens, et le dépôt aurait pu passer une journée
à réécrire des fiches pour creuser un écart. Et **deux cas types ne répondent
pas à leur âge d'entrée**, ce que le script mesure au lieu de le supposer :
l'exploitant agricole et la profession libérale relèvent de régimes en points,
auxquels le modèle n'oppose aucune durée requise — `trimestres_requis` vaut
zéro, leur départ suit l'âge légal, et le déplacer de huit ans d'âge d'entrée
n'y change pas un trimestre.

**Ce qui reste.** Le +0,61 point du système actuel mêle deux effets, l'âge de
départ et la durée de carrière, parce que déplacer l'entrée déplace les deux —
et c'est la durée qui domine, quatre des six cas types déplacés entrant plus
tôt. Les séparer demanderait un levier que la grille n'a pas. Les deux cas
types en points gardent leurs écarts, −1,21 et +0,66 an, qui viennent d'ailleurs
— vraisemblablement de la décote de ces régimes, que le modèle ne leur applique
pas.

**Fichiers.** `scripts/cout_age_depart.py`, `tests/test_cout_age_depart.py`,
`scripts/age_conjoncturel.py` (deux fonctions rendues rejouables sur une autre
grille), `docs/limites.md` § 5 ter.

### 84. Le versant inverse porté sur le site, et deux dettes trouvées en confrontant les listes — `fait`

**Demande.** « Que peut-on faire de plus ? », puis trois chantiers retenus :
porter le versant « cotisation » sur le site, lire les bascules du code des
pensions, confronter l'inventaire à la liste légale.

**Le code des pensions, dix bascules.** La recherche documentaire sur le web
n'avait rien rendu sur ce terrain ; l'index LEGI du dépôt porte les versions, et
la méthode qui avait donné L. 135-2 y suffit. En 2004, le b de L. 12 passe de
« bonification accordée AUX FEMMES FONCTIONNAIRES » à « les fonctionnaires et
militaires […] à condition qu'ils aient INTERROMPU leur activité », et se ferme
aux enfants nés depuis : un an de services gratuits devient un an payé par une
interruption de carrière. C'est la seule fois, dans tout ce chantier, qu'un
avantage devient contributif au sens fort. En 2011, trois fermetures le même
jour : le départ anticipé des parents de trois enfants quitte L. 24 et n'y est
jamais revenu, la catégorie active et le cinquième militaire passent de quinze à
dix-sept ans de services.

**Et le partage qui en sort renverse la conclusion précédente.** L'action 78
concluait que « la frontière ne recule pas ». C'est vrai du code de la sécurité
sociale — cinq ouvertures, une fermeture qui n'en est pas une — et faux du code
des pensions : six fermetures contre quatre ouvertures. **La fonction publique
est le seul endroit où la frontière a reculé.** Une dissymétrie qu'aucune des
deux listes ne montre seule.

**Une question `a_verifier` du registre de veille, tranchée.** Le décret
n° 2026-699 crée une bonification d'un trimestre pour les enfants nés depuis
2004 : est-ce un ajout aux deux trimestres de L. 12 bis ? **Non.** L. 12 bis,
réécrit le même jour, dit que des deux trimestres « l'un est pris en compte au
titre de la bonification prévue au b ter ». Le total ne bouge pas ; un trimestre
passe de la durée d'assurance aux SERVICES, où il entre dans la liquidation.

**La confrontation à la liste légale, et deux dettes.** Les huit postes de
L. 222-2-1 ont été confrontés à l'inventaire. L'**apprentissage** manquait, et
ne pouvait pas manquer autrement : son droit est dans le code du travail, et les
trois listes internes dont l'inventaire est né décrivent ce que le modèle sait
faire. Les **périodes reconnues équivalentes** manquaient aussi, et leur poste
vient d'être abrogé. Trouvaille latérale : le 4° fait payer par la branche
vieillesse les points de complémentaire des préretraites et de l'ASS — le
dispositif était dans l'inventaire, son payeur n'y était pas. Et le 2° ne
finance que trois des neuf catégories de périodes de L. 351-3 : les sportifs de
haut niveau et les TUC, les deux droits les plus récemment ouverts, sont à la
charge des régimes, sans payeur nommé.

**Le site, enfin.** Une quatrième carte sur la page Avantages : « Et l'inverse :
que cotise-t-on sans rien acquérir ? » Elle porte les 17,9 Md€ depuis 1997, le
tableau des tranches Agirc-Arrco, et dit que les deux grandeurs ne se
soustraient pas. Le calcul vit dans `src/retraite_notionnelle/frontiere.py` et
n'est PAS porté en JavaScript : il ne dépend d'aucune saisie, le paquet le
transporte déjà fait, et le portage le relit. C'est la règle du dépôt — un
chiffre ne dépend pas de la porte — appliquée au moins cher.

**Quatre garde-fous se sont déclenchés, et chacun a servi.** Le port JavaScript
graduait son axe sur la plus haute bande au lieu de leur somme, parce que
`graphique` prend ses options en positionnel et qu'un objet les laissait à
faux ; `pourcentage` n'a pas la même signature des deux côtés, d'où un « 27,0 % »
contre « 27 % ». Les deux ont été trouvés par la comparaison HTML, au caractère
près. Le compteur d'incises en tiret a fait resserrer cinq phrases. Et le
catalogue des affirmations a exigé six contrôles pour six phrases fortes, dont
un qui interdit au calcul de glisser un facteur dans l'assiette — l'erreur même
que la carte dénonce.

**Le budget de lecture de la page a été relevé, et c'est la seule fois.** Elle
était à 1 997 mots pour un plafond de 2 000 : aucune carte, si brève soit-elle,
ne pouvait plus y entrer. Le plafond passe à 2 250, avec la raison écrite dans
le test. Replier la réponse aurait été pire que l'écrire : c'est le seul endroit
du site qui dise que le compte n'est pas à sens unique.

**Fichiers.** `src/retraite_notionnelle/frontiere.py`, `moteur/js/frontiere.js`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`, `index.html`,
`scripts/construire_donnees.py`,
`data/reference/legislation/frontiere_contributive.yaml`,
`data/reference/site/affirmations.yaml`, `tests/test_affirmations.py`,
`tests/test_web.py`, `tests/test_frontiere_contributive.py`,
`docs/frontiere_contributive.md`.

### 85. Le relevé de carrière se dépose en PDF, et le navigateur le lit — `fait`

**Pourquoi.** L'action 7 avait ouvert la saisie exacte — une ligne par année,
`année:régime:revenu:trimestres` — et `limites.md` §5 déclarait l'import
automatique impossible. Il l'est en effet par la voie qu'on regardait : le
répertoire de gestion des carrières uniques n'est pas ouvert, et son accès
demande les identifiants de l'assuré. Mais ce n'est pas la seule voie. **Le
document existe déjà**, en PDF, sur le compte retraite de chacun, et rien
n'oblige à aller le chercher : c'est l'assuré qui le télécharge, et le
navigateur qui le lit. Ce qui fermait la saisie exacte à presque tout le monde
n'était pas l'authentification, c'était la recopie de quarante-cinq lignes de
chiffres.

**Marche.** Trois briques, et chacune a son modèle de référence en Python.

- *Le lecteur de PDF, porté dans le navigateur.* `scripts/fetch/lecture_pdf.py`
  lit les PDF du dépôt depuis les barèmes de la CNBF ; `moteur/js/lecture-pdf.js`
  en est le portage, fonction pour fonction. Deux écarts imposés par le
  navigateur, et deux seulement : la décompression y est asynchrone
  (`DecompressionStream`, qui remplace `zlib`), et les octets sont portés par
  une chaîne latin-1, ce qui permet de reprendre mot pour mot les expressions
  régulières binaires du modèle. Vérifié sur deux vrais documents — le rapport
  de l'OPEF, 6 054 lignes, et le guide « Comment lire mon relevé de carrière »
  de l'Assurance retraite, 318 lignes — : les deux lecteurs rendent la même
  chose, ligne pour ligne.
- *La lecture du relevé.* `src/retraite_notionnelle/web/releve_lu.py` fait foi,
  `moteur/js/releve-lu.js` le porte, et `tests/test_releve_lu.py` fait tourner
  les deux sur les mêmes relevés en comparant la saisie qu'ils rendent au
  caractère près. Quatre règles : un titre de régime vaut pour les lignes qui
  suivent ; une ligne de carrière porte son année, un revenu au-dessus de
  quatre et des trimestres au plus égaux à quatre ; une année revient autant
  de fois que le relevé la coupe par employeur, et les revenus s'additionnent ;
  ce qui n'est pas compris ressort tel quel et s'affiche.
- *Le dépôt.* Un champ de fichier et un glisser-déposer dans le formulaire, et
  le gestionnaire dans `index.html`. Les deux modules sont chargés à la
  demande, jamais préchargés : ils ne servent qu'à qui dépose un relevé, et le
  test des `modulepreload` l'exige maintenant dans les deux sens.

**Ce que ça déplace.** Aucun chiffre du modèle : ni témoin de simulation, ni
paramètre. Ce qui change est ce que le site SAIT recevoir. Quatre choses que
la lecture fait et qu'une recopie à la main ne faisait pas : **les francs sont
convertis** (÷ 6,55957, et ÷ 655,957 avant 1960, qu'un relevé porte en anciens
francs — le guide de l'Assurance retraite le dit de la table qu'il publie en
regard) ; **les périodes assimilées deviennent des interruptions**, par plages
fusionnées, dans le champ prévu ; **les points Agirc disent le cadre**, année
par année, ce qu'aucune colonne du régime général ne dit ; et **la date de
naissance est reprise de l'en-tête**, la seule donnée du formulaire, hors la
carrière, que le document porte.

**Deux défauts trouvés en chemin, et corrigés.** Le lecteur de référence ne
traitait pas `BT` : la norme y remet la matrice de texte à l'identité, et un
producteur qui ouvre un objet texte par ligne — c'est ainsi que sont faits les
relevés — voyait ses ordonnées s'ADDITIONNER d'un bloc au suivant. Le document
sortait à l'envers, une ligne par fragment. Corrigé des deux côtés, avec son
cas d'essai ; les deux vrais documents n'en bougent pas d'une ligne. Et la
première version lisait n'importe quel PDF : le rapport de l'OPEF, cent pages
sans le moindre relevé, y rendait vingt-deux « années de carrière » qui
n'avaient jamais existé. Un document doit maintenant se reconnaître — son
titre, ou l'en-tête de la colonne des trimestres — sans quoi rien n'est lu.

**Ce qui reste.** Ce que le relevé ne porte pas : le mois, le revenu au-delà du
plafond de la Sécurité sociale, le revenu des régimes qui comptent en points,
et la répartition d'un état de services couvrant plusieurs années. Les quatre
sont dits à qui dépose son relevé et écrits dans `limites.md` §5. Reste aussi à
confronter la lecture à de VRAIS relevés : ceux du dépôt sont écrits à la forme
des documents officiels, non tirés d'eux — aucun relevé réel n'est public, et
il n'y en a pas dans le dépôt. Une mise en page inconnue se voit tout de suite
— le compte rendu dit combien d'années ont été lues et montre les lignes qu'il
n'a pas comprises —, et c'est ce compte rendu qui dira quoi corriger.

**Fichiers.** `moteur/js/lecture-pdf.js`, `moteur/js/releve-lu.js`,
`src/retraite_notionnelle/web/releve_lu.py`, `scripts/fetch/lecture_pdf.py`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`src/retraite_notionnelle/web/gabarit.py`, `index.html`,
`tests/test_releve_lu.py`, `tests/test_lecture_pdf.py`,
`tests/js/lecture-pdf.test.js`, `tests/js/comparer-releve.mjs`,
`tests/test_web.py`, `docs/limites.md` §5.

### 86. Une carrière tout en points partait au taux plein sans l'avoir — `fait`

**Pourquoi.** L'action 83 avait buté sur deux cas types dont l'âge de départ ne
répondait pas à leur âge d'entrée, et s'était contentée de le constater :
« l'exploitant agricole et la profession libérale relèvent de régimes EN
POINTS, auxquels le modèle n'oppose aucune durée requise ». Le constat était
juste, l'explication fausse — et elle recouvrait un défaut du moteur.

**Ce que c'était vraiment.** Le coefficient de réduction était DÉJÀ appliqué :
`_abattement_points` lit la décote de la fiche, et les fiches `cnavpl` et
`msa_non_salaries` portent depuis toujours `duree_requise_trimestres` et
`decote_par_trimestre`. Ce qui manquait est que la règle qui DATE le départ ne
le voyait pas : `age_taux_plein_droit` rendait l'âge d'ouverture dès que la
carrière n'avait aucune période en annuités — `if not annuites: return
ouverture`. Le modèle faisait donc liquider « au taux plein » des carrières
qu'il servait minorées. Le libéral né en 1955 partait à soixante-quatre ans
avec cent quarante-huit trimestres sur cent soixante-six requis : dix-huit
trimestres de réduction que la règle disait inexistants.

**Le droit, lu ce jour.** L. 643-3 I du code de la sécurité sociale
(LEGIARTI000053280388, version du 31 décembre 2025 issue de la loi
n° 2025-1403, applicable aux pensions prenant effet à compter du 1er septembre
2026) : la pension vaut « le produit de la valeur du point par le nombre de
points acquis » quand l'assuré a « la durée d'assurance fixée en application du
deuxième alinéa de l'article L. 351-1 dans le présent régime et dans un ou
plusieurs autres régimes », et un décret « fixe les coefficients de réduction
[…] lorsque l'intéressé ne justifie pas de la durée ». Le II de l'article
L. 732-24 du code rural (LEGIARTI000053280317) dit la même chose pour les
non-salariés agricoles. Ligne et journal dans `veille.yaml`.

**Ce que ça a déplacé.** Presque rien en chiffres, et c'est voulu : la
trajectoire 2070 reste à 18,35 % du PIB, les 469 témoins de simulation ne
bougent pas d'un bit, et seul l'exploitant agricole se déplace — 61,64 à
61,73 ans de moyenne sur 2013-2020. Ce qui change est que le modèle ne dit plus
« taux plein » d'une pension qu'il minore.

**Le défaut en masquait un second, et c'est le plus intéressant.** Corrigé, le
taux plein faisait partir la profession libérale à SOIXANTE-NEUF ANS : entrée à
vingt-sept ans sans carrière antérieure, elle n'atteint la durée requise à
aucun âge, et la règle la renvoyait à l'annulation de la décote, plus les deux
ans de sa fiche. Or sa fiche disait déjà ce qu'il fallait faire — « seul cas
type à partir APRÈS l'âge d'ouverture : deux ans » —, et elle portait pourtant
`regle_liquidation: taux_plein`, qui ne donnait « ouverture + deux ans » que
par le défaut qu'on venait de corriger. Elle porte désormais
`regle_liquidation: ouverture`, ce que sa propre phrase disait ; et la DREES
tranche dans le même sens, les professions libérales partant à 62,6 ans en
moyenne de 2013 à 2020, non à soixante-sept.

**Trois leçons.** **Un constat n'est pas une explication** : l'action 83 avait
mesuré l'insensibilité et en avait déduit une cause plausible et fausse ; il a
suffi de lire le moteur pour voir que la décote y était et que c'était la règle
d'âge qui ne la lisait pas. **Une correction en expose une autre** : rendre la
règle juste a rendu fausse une phrase de fiche, qu'il a fallu remettre d'accord
avec elle-même. Et **une correction se borne** : étendre au passage le départ
anticipé pour carrière longue aux périodes en points faisait rendre au taux
plein un âge ANTÉRIEUR à celui que l'ouverture accorde — soixante-trois ans
contre soixante-quatre pour un chef d'exploitation né en 2000 —, les deux
règles se contredisant. La carrière longue reste donc lue sur les seules
périodes en annuités, et le commentaire dit pourquoi.

**Ce qui reste.** Les coefficients de réduction eux-mêmes ne sont pas lus dans
leur décret en Conseil d'État : les deux fiches portent 1,25 % par trimestre,
aligné sur le régime général, et rien ne dit que les barèmes coïncident —
R. 643-8 pour la CNAVPL, la section D. 732 pour la MSA. Ce que la carrière
longue ouvre à un régime en points n'est pas tranché. Et le cas type libéral
n'a toujours aucune année salariée avant son installation, quand un libéral
réel en a : c'est ce qui le met hors d'atteinte de la durée requise.

**Fichiers.** `src/retraite_notionnelle/scenarios/actuel.py`,
`src/retraite_notionnelle/castypes.py`, `moteur/js/scenario-actuel.js`,
`moteur/js/castypes.js`, `data/reference/legislation/veille.yaml`,
`tests/test_cout_age_depart.py`, `docs/limites.md` § 5 ter,
`tests/temoins/pages.json`.

### 87. Ce qu'une carrière tout en points ne se voyait rien opposer — `fait`

**Demande.** « Vas-y, charge-toi de ça » : les trois réserves laissées par
l'action 86 — lire le barème du coefficient de réduction dans son décret, dire
ce que la carrière longue ouvre à un régime en points, et regarder le cas type
libéral sans carrière antérieure.

**Ce que les textes disent.** **R. 643-7 CSS**, version du 1er septembre 2023 :
la réduction est fonction « soit du nombre de trimestres correspondant à la
durée séparant l'âge auquel la pension de retraite prend effet du
soixante-cinquième anniversaire […] soit du nombre de trimestres
supplémentaires qui serait nécessaire […] pour relever du deuxième alinéa du I
de l'article L. 643-3 », arrondi au chiffre supérieur, « le plus petit de ces
deux nombres est pris en considération », et « le coefficient de minoration est
égal à 1,25 % par trimestre manquant dans la limite de vingt trimestres ».
C'est mot pour mot ce que `_trimestres_de_decote` faisait déjà : **la
transcription de la fiche `cnavpl` est confirmée, et rien n'a bougé.** Côté
agricole, R. 732-39 du code rural pose la même condition mais non le taux, et
l'article qui le porte n'est pas dans le champ social de l'index : la fiche
`msa_non_salaries` garde son 1,25 % par transcription, et la ligne de veille le
dit.

**La carrière longue leur est ouverte, et par deux textes.** L. 732-18-1 du
code rural abaisse l'âge « pour les personnes ayant exercé une activité non
salariée agricole qui ont commencé leur activité avant un des quatre âges, dont
le plus élevé ne peut excéder vingt et un ans » ; le II de L. 643-3 renvoie les
professions libérales à L. 351-1-1. Le moteur ne l'offrait qu'aux périodes en
annuités. Les deux règles d'âge la lisent désormais sur la même liste — ne
l'ouvrir qu'au taux plein faisait rendre à celui-ci un âge ANTÉRIEUR à celui que
l'ouverture accordait, soixante-trois ans contre soixante-quatre pour un chef
d'exploitation né en 2000.

**Et en cherchant cela, le défaut le plus visible des trois.** `calculer` ne
lisait l'âge d'ouverture opposable que sur les périodes en annuités. Une
carrière entière en points n'en ayant aucune, **aucun âge ne lui était
opposé** : le simulateur du site servait une pension de chef d'exploitation ou
de profession libérale **à cinquante ans** sans rien refuser, quand il la
refusait à l'artisan de la page voisine. Ce n'était pas un défaut de cas type,
c'était une réponse fausse donnée à un visiteur. Au passage, `requis_reference`
retombait pour eux sur 160 trimestres — une durée que plus aucune génération ne
doit —, et c'est elle que leur abattement opposait. Corrigé par une SECONDE
PASSE qui ne s'ouvre que si la première n'a rien trouvé : les carrières en
annuités ne bougent pas d'un trimestre.

**Ce que ça a déplacé.** Rien sur les agrégats — trajectoire 2070 à 18,35 % du
PIB, écart moyen à l'âge conjoncturel tous régimes à −0,07 an, et le
contrefactuel de l'action 83 tient : les cinq scénarios notionnels bougent de
moins d'un dixième de point, le système actuel de +0,59, et corriger les âges
éloigne toujours du COR. Les témoins de SIMULATION bougent, eux, et c'est le
sujet : ce sont les carrières tout en points, qui voient maintenant un âge, une
durée et une carrière longue. Le chef d'exploitation part à soixante-trois ans
pour les générations récentes, sa carte de la page Cas types passe de +10 % à
+5 %, et l'écart aux militaires de 54 à 50 points.

**L'angle mort du contrefactuel est refermé.** L'action 83 comptait deux cas
types « insensibles à leur âge d'entrée » ; il n'y en a plus aucun, et les neuf
comparables répondent tous.

**Trois leçons.** **Une réserve bien écrite est un plan de travail** : les
trois lignes laissées par l'action 86 ont donné trois lectures et un défaut
qu'aucune ne nommait. **Un défaut de datation cachait un défaut de service** :
ce qui n'était qu'une bizarrerie de cas type — un âge qui ne bouge pas — était
la même cause qu'une pension servie à cinquante ans sur le site. Et **une
seconde passe vaut mieux qu'un élargissement** : n'ouvrir la boucle aux régimes
en points que si les annuités n'ont rien donné garantit que rien d'autre ne
bouge, et le test le dit.

**Ce qui reste.** Le taux du coefficient agricole, faute d'article dans le
champ social de l'index. Et le cas type libéral n'a toujours aucune année
salariée avant son installation, ce qui le met hors d'atteinte de la durée
requise à tout âge : sa fiche date donc son départ sur l'ouverture, et savoir
si un libéral représentatif a une carrière antérieure — l'internat, le
salariat — reste ouvert. La DREES le laisse penser, en donnant 62,6 ans de
moyenne aux professions libérales là où la fiche, seule, ne peut jamais
atteindre la durée.

**Fichiers.** `src/retraite_notionnelle/scenarios/actuel.py`,
`moteur/js/scenario-actuel.js`, `data/reference/legislation/veille.yaml`,
`scripts/cout_age_depart.py`, `tests/test_cout_age_depart.py`,
`docs/limites.md` § 5 ter, `tests/temoins/simulations.json`,
`tests/temoins/pages.json`.

### 88. Une bonification n'est pas une majoration : 1,2 % de pension rendus au droit — `fait`

**Demande.** « Que peut-on faire de plus ? », puis trois chantiers : combler les
deux dettes de l'inventaire, modéliser le trimestre qui change de case, lire les
régimes spéciaux.

**Une ligne du registre était restée ouverte alors qu'elle était résolue.**
L'action 84 avait répondu à la question que `veille.yaml` posait sur le décret
n° 2026-699 — est-ce un ajout aux deux trimestres de L. 12 bis ? non — sans
refermer la ligne. C'est fait, et la refermer a révélé le reste.

**Le modèle sur-créditait les mères fonctionnaires depuis 2004, et personne ne
l'avait vu.** L'article L. 12 b du code des pensions accorde une BONIFICATION,
qui s'ajoute aux services et relève donc le prorata, c'est-à-dire la pension.
L'article L. 12 bis, qui lui succède pour les enfants nés depuis 2004, accorde
une MAJORATION DE DURÉE D'ASSURANCE, qui ne joue que sur la décote et la durée
tous régimes. Le moteur les traitait de la même façon : il portait les deux
trimestres au prorata de la fonction publique.

**La preuve que la distinction est la bonne est dans la réforme qui la
déplace.** L'article 104 de la loi du 30 décembre 2025 crée un b ter à L. 12
pour convertir UN des deux trimestres en bonification, et réécrit L. 12 bis le
même jour pour dire que des deux trimestres « l'un est pris en compte au titre
de la bonification prévue au b ter ». Une conversion n'a de sens que si les deux
cases diffèrent.

**Ce que la correction déplace.** Sur un témoin du dépôt — mère fonctionnaire
d'État de trois enfants —, les services passent de 142 à 139 trimestres et la
pension annuelle de 46 938 à 45 946 €, soit **−2,1 %**. Sur une mère de deux
enfants, **−1,16 %**, et le taux est stable d'une génération à l'autre parce
qu'il ne dépend que du nombre de trimestres retirés sur la durée requise.
L'agrégat, lui, ne bouge pas : aucun des treize cas types n'est à la fois
fonctionnaire et parent — le même défaut de grille que la majoration pour trois
enfants.

**La table porte deux colonnes de plus**, `services_par_enfant` et
`services_depuis`, parce qu'il fallait DEUX horloges : le montant se lit à
l'année de naissance de l'enfant, la conversion à l'année de liquidation. Une
approximation est assumée et écrite : le b ter vaut pour les pensions prenant
effet à compter du 1er septembre 2026, le modèle date à l'année et l'applique
dès janvier — huit mois de trop, sur une génération, pour un trimestre.

**Les deux dettes de l'action 84 sont comblées, et la seconde n'était pas ce
qu'on croyait.** L'apprentissage a sa ligne, fondée sur le second alinéa de
L. 6243-3 du code du travail. Et L. 351-7-1, que le poste abrogé désignait comme
« périodes reconnues équivalentes », vise en réalité les SERVICES MILITAIRES EN
AFRIQUE DU NORD, à qui il ouvre une réduction de la durée requise. L'article est
toujours en vigueur alors que le poste qui le finançait est abrogé : c'est le
troisième cas, après les indemnités journalières de maternité et le minimum
contributif, où un droit survit à son financement. L'inventaire compte
désormais quarante-cinq dispositifs.

**Les régimes spéciaux, six bascules, et une régularité.** Les bonifications de
conduite de la SNCF et du tableau B de la RATP se ferment aux entrants d'après
le 1er janvier 2009 dès la rédaction initiale des décrets de 2008 — c'est le
seul cas du fichier où une fermeture se lit dans le texte qui l'institue et non
dans l'écart entre deux versions. Puis elles ne font plus que s'élargir, trois
fois : l'activité partielle en 2020, les emplois équivalents à la RATP en 2025,
le congé de mobilité à la SNCF le 7 août 2026 — le déplacement le plus récent
que le dépôt porte, toutes faces confondues.

**Le chômage partiel de 2020 a élargi un avantage non contributif sans que
personne ne l'ait décidé comme tel.** Le décret du 1er décembre 2020 fait
compter les périodes d'activité partielle « pour le calcul de ces
bonifications » : un mois de chômage partiel vaut un mois de conduite, pour un
droit qui n'a jamais été cotisé. Rien dans le texte ne le présente ainsi.

**Le portrait d'ensemble se nuance, et c'est la troisième fois.** L'action 78
concluait que la frontière ne recule pas ; l'action 84 a montré que c'était vrai
du privé et faux de la fonction publique. Les régimes spéciaux, eux, sont à
l'équilibre — trois ouvertures, trois fermetures — et d'une façon qui leur est
propre : fermés d'un coup, élargis ensuite pour ceux qui restaient.

**Et le plafond desserré la veille a été mieux que rendu.** L'action 84 avait
relevé le budget de lecture de la page Avantages de 2 000 à 2 250 mots, faute de
place pour une carte de plus, et l'avait signalé comme un desserrage. Deux
dispositifs ajoutés le lendemain le faisaient à nouveau sauter — et montraient le
défaut : les sept tableaux de l'inventaire, ouverts à dessein, consommaient la
moitié du budget. Un tableau se parcourt, une phrase se lit. Les deux sont
désormais mesurés à part, sur les dix pages ; la prose de la page Avantages est
tenue à 1 300 mots, soit moins que les 2 000 d'avant le desserrage ; et le
budget de ses tableaux se calcule sur l'inventaire, à trente mots par ligne, de
sorte qu'en allonger la liste — c'est-à-dire faire le travail que cette page
existe pour montrer — ne coûte plus une phrase à personne.

**Fichiers.** `data/reference/legislation/majoration_duree_assurance.csv`,
`src/retraite_notionnelle/scenarios/actuel.py`, `moteur/js/regimes.js`,
`moteur/js/scenario-actuel.js`, `scripts/construire_donnees.py`,
`data/reference/legislation/avantages_non_contributifs.yaml`,
`data/reference/legislation/frontiere_contributive.yaml`,
`scripts/frontiere_contributive.py`, `tests/test_scenarios_meres.py`,
`tests/test_frontiere_contributive.py`, `tests/test_web.py`,
`docs/frontiere_contributive.md`, `docs/parcours_presentation.md`,
`data/reference/legislation/veille.yaml`.

---

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

### 90. Le barème agricole retrouvé, et un groupe qui ne décrivait pas le libéral — `fait`

**Demande.** « Fais des recherches complémentaires et corrige » : les deux
réserves de l'action 87 — le taux du coefficient de minoration agricole, que
l'index n'avait pas rendu, et le cas type libéral sans carrière antérieure.

**Le barème agricole n'était pas introuvable, la requête l'était.**
`dila_cherche.py` interroge l'index en plein texte, et ses requêtes ne
rendaient rien. La même base, interrogée en SQL sur le titre du code, donne
262 articles `D732`/`R732`, dont 43 contiennent « minoration ». **R. 732-61**,
dans sa version du 28 octobre 2017 en vigueur jusqu'au 1er janvier 2026,
porte le barème en toutes lettres : « La minoration est égale au produit du
plus petit de ces deux nombres, arrondis chacun au nombre immédiatement
supérieur, par le coefficient suivant : −2,5 % pour l'assuré né avant le
1er janvier 1944 […] −1,25 % pour l'assuré né après 1952. »

**Il est GÉNÉRATIONNEL, et c'est celui du régime général.** Les onze valeurs
sont, génération par génération, celles du II de R. 351-27 que
`coefficient_minoration.csv` porte déjà — et la fiche `msa_non_salaries`
portant `decote_par_generation: true`, le modèle les appliquait depuis
toujours. Son `decote_par_trimestre: 0.0125` n'est que le repli. **La
transcription est confirmée, et aucune valeur ne bouge.** Depuis le 1er janvier
2026, R. 732-68 rend l'alignement explicite — « déterminé dans les mêmes
conditions que celui mentionné au 2° du I de l'article R. 351-27 ».

**Et le recueil de la CNAVPL a démenti une phrase écrite la veille.** L'action
86 justifiait la règle de départ du cas type libéral en écrivant que « la DREES
observe les professions libérales partir à 62,6 ans en moyenne ». C'est le
GROUPE 3 de la nomenclature — « cadres et professions intellectuelles
supérieures » —, dominé par les cadres salariés. La caisse des libéraux publie
l'âge de ses propres titulaires : **64,81 ans en 2018, 66,11 en 2025**. Trois
ans et demi d'écart avec son groupe.

**Le signe s'inverse.** Confronté au chiffre de sa caisse plutôt qu'à celui de
son groupe, le cas type part **1,24 an trop TÔT** en moyenne de 2018 à 2025, là
où le groupe 3 le disait 0,66 an trop tard. Il est donc sorti du champ de la
confrontation par catégorie, avec sa raison et ses chiffres écrits dans
`cas_types_csp.yaml` ; huit cas types y restent, et l'écart pesé en valeur
absolue passe de 1,16 à 1,17 an.

**La décision de l'action 86 reste la bonne, pour une meilleure raison.** Dater
le départ de ce cas type sur l'âge d'OUVERTURE et non sur le taux plein le fait
partir à soixante-quatre puis soixante-six ans ; le taux plein le ferait
attendre soixante-neuf. Sa caisse observe soixante-six.

**Trois leçons.** **Une recherche qui ne rend rien n'est pas une absence** : le
plein texte de l'index taisait un article que le SQL a rendu en une requête, et
le dépôt a passé une journée à écrire « non lu » d'un texte qu'il portait.
**Un groupe de nomenclature n'est pas toujours la bonne référence** : celui du
libéral le classe correctement et le décrit mal, et c'est exactement le genre
d'erreur qu'un couloir large ne rattrape pas — il faut une autre source. Et
**une justification fausse peut soutenir une décision juste** : la règle
d'ouverture était le bon choix, la raison qu'on lui donnait ne l'était pas, et
seule la seconde a dû changer.

**Ce qui reste.** Le PLAFOND de vingt trimestres n'est explicite que chez les
libéraux (R. 643-7) ; ni R. 351-27 2° ni R. 732-61 n'en portent, et le modèle
en applique un partout. Il ne mord que sur un départ de plus de cinq ans avant
l'âge d'annulation, où la décote ne s'applique pas — mais c'est à trancher sur
texte, et la ligne de veille le dit. Et le cas type libéral n'a toujours aucune
carrière antérieure, quand la CNAVPL immatricule ses affiliés à **32,58 ans en
moyenne** : dix ans de carrière ailleurs avant l'installation. `CasType` ne
porte qu'une affiliation, et lui en donner deux est un chantier, non une
retouche.

**Fichiers.** `data/reference/legislation/veille.yaml`,
`data/reference/macro/cas_types_csp.yaml`,
`src/retraite_notionnelle/castypes.py`, `moteur/js/castypes.js`,
`tests/test_age_depart_csp.py`, `tests/test_cout_age_depart.py`,
`docs/limites.md` § 5 ter.

### 91. Cinq ans de chômage ne coûtaient rien à un fonctionnaire — `fait`

**Demande.** « Que peut-on faire d'autre ? », puis trois chantiers, dont le
premier : auditer la même confusion ailleurs — durée contre services, pour les
périodes assimilées cette fois.

**La confusion était plus large que la majoration pour enfants.** L'action 88
avait séparé la bonification, qui entre aux services, de la majoration de durée
d'assurance, qui n'y entre pas. Restait à regarder d'où viennent les AUTRES
trimestres du prorata de la fonction publique : le moteur y portait toute
période validant un trimestre, chômage compris. Une carrière de fonctionnaire
d'État coupée de cinq ans de chômage servait donc exactement la même pension
qu'une carrière pleine — au centime près, ce qui est la signature d'un droit
qu'on n'a pas écrit plutôt que d'un droit généreux.

**Ce que disent L. 5 et L. 9, lus dans LEGI.** L'article L. 13 proratise la
pension de l'État sur les SERVICES ET BONIFICATIONS, non sur la durée
d'assurance ; et l'article L. 9, version LEGIARTI000053279095, est catégorique :
« Le temps passé dans une position statutaire ne comportant pas
l'accomplissement de services effectifs au sens de l'article L. 5 ne peut entrer
en compte dans la constitution du droit à pension, sauf : 1° Dans la limite de
trois ans par enfant né ou adopté à partir du 1er janvier 2004 […] ». Suit une
liste fermée — congé parental, temps partiel de droit et disponibilité pour
élever un enfant ; congés de maladie, de maternité, d'accident de service et de
maladie professionnelle du fonctionnaire en activité ; congés de formation et
congé civique ; détachement. Le chômage n'y est pas, et pour cause : un
fonctionnaire au chômage n'est plus fonctionnaire, le chômage n'est pas une
position statutaire.

**La règle est en données, pas en code.** `periodes_non_travaillees.csv` porte
deux colonnes de plus, `services_fonction_publique` — `oui`, `non`, `plafonne` —
et `services_plafond_annees_par_enfant`. Le moteur tient désormais deux comptes
parallèles par régime, la durée d'assurance et les services, et choisit le
numérateur sur la famille du régime : services dans la fonction publique, durée
d'assurance partout ailleurs. Le budget des services plafonnés se tient sur
TOUTE la carrière, et non année par année : deux congés de deux ans pour un seul
enfant n'ouvrent que trois ans de services.

**Ce que la correction déplace.** Sur une fonctionnaire d'État née en 1975,
partie à soixante-quatre ans, cinq ans de chômage retirent vingt trimestres de
services : 148/172 au lieu de 168/172, et 42 422 € au lieu de 48 155 €, soit
−11,9 %. Deux ans en retirent 4,76 %. Le congé parental, lui, ne coûte rien à
une mère de deux enfants — L. 9 l'excepte à hauteur de trois ans par enfant —
mais coûte huit trimestres à une mère d'un seul. Et rien ne bouge au régime
général : les mêmes cinq ans y restent vingt trimestres assimilés, le prorata de
la CNAV portant sur la durée d'assurance. Aucun témoin du dépôt ne change de
chiffre, aucun cas type n'étant à la fois fonctionnaire et interrompu — c'est
précisément pourquoi le défaut avait tenu si longtemps.

**Deux approximations assumées, écrites toutes les deux.** La condition « né ou
adopté à partir du 1er janvier 2004 » du 1° n'est pas appliquée, le modèle ne
collectant pas l'année de naissance des enfants. Et les dix-huit régimes
spéciaux, qui se proratisent eux aussi sur des services, gardent l'ancienne
règle : leurs règlements n'ont pas été lus, et `docs/limites.md` le dit.

**Fichiers.** `data/reference/legislation/periodes_non_travaillees.csv`,
`src/retraite_notionnelle/donnees/chargement.py`,
`src/retraite_notionnelle/carriere.py`,
`src/retraite_notionnelle/scenarios/actuel.py`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/carriere.js`,
`moteur/js/scenario-actuel.js`, `moteur/js/pages.js`,
`scripts/construire_donnees.py`, `tests/test_services_fonction_publique.py`,
`data/reference/legislation/veille.yaml`, `docs/methodologie.md`,
`docs/limites.md`, `README.md`.

### 92. Une année de chômage fermait un départ que le droit ouvre — `fait`

**Demande.** « Que peut-on faire d'autre ? », et le troisième chantier : les
trois lignes du registre de veille restées `manque`. Celle-ci est la première.

**Ce que le registre disait, et depuis quand.** `carriere_longue_reputes_cotises_autres`
portait l'état `manque` depuis le 17 septembre 2026 : le départ anticipé pour
carrière longue ne compte pas la durée d'assurance mais celle « ayant donné lieu
à cotisations à la charge de l'assuré » (D. 351-1-1), et le modèle s'en tenait là
— aux seuls trimestres réellement cotisés, plus les deux trimestres d'enfants que
la loi de financement pour 2026 répute cotisés. La conséquence était mesurable et
fausse : **une seule année de chômage indemnisé suffisait à fermer un départ que
le droit ouvre.**

**L'article qui manquait, lu dans l'index LEGI.** D. 351-1-2, version
LEGIARTI000053356011, réputé cotisées six familles de périodes, chacune sous sa
propre limite, comptée sur toute la carrière et tous régimes confondus :

| Ce que le décret répute cotisé | Renvoi | Limite |
|---|---|---|
| service national | 1° du I | 4 trimestres |
| incapacité temporaire — maladie ET accident du travail | 2° (R. 351-12, 1° et 5°) | 4 trimestres **pour les deux** |
| chômage indemnisé et activité partielle | 3° (R. 351-12, b et c du 4°, et 10°) | 4 trimestres |
| maternité | 4° (R. 351-12, 2°) | **aucune** |
| invalidité | 5° (R. 351-12, 3°) | 2 trimestres |
| parents au foyer et aidants (AVPF) | 7° (L. 381-1 et L. 381-2) | 4 trimestres |

Deux lectures décident de tout, et aucune ne se devine. La première : le 2° vise
l'INCAPACITÉ TEMPORAIRE, non la maladie puis l'accident du travail — les deux
motifs tiennent ensemble dans quatre trimestres, et les compter séparément en
aurait rendu huit. La seconde : le 3° ne cite que les b et c du 4° de R. 351-12,
jamais le d, qui est le chômage NON indemnisé. Celui-là valide des trimestres
d'assurance et n'en répute aucun cotisé — c'est la seule période assimilée que le
décret ne reprenne jamais, et la maternité est la seule qu'il n'écrête pas.

**La règle est en données.** `periodes_non_travaillees.csv` porte deux colonnes
de plus, `reputes_cotises_enveloppe` et `reputes_cotises_plafond` : l'enveloppe
est ce qui porte la limite, et deux motifs qui la partagent la partagent
vraiment. Le budget se consomme dans l'ordre de la carrière. Le plafond annuel de
quatre trimestres que l'article pose par ailleurs est tenu d'avance, une année du
modèle ne portant qu'un statut.

**Deux témoins neufs, pour une raison qui vaut d'être dite.** Aucun cas type du
dépôt n'était à la fois interrompu et candidat à la carrière longue, ni à la fois
fonctionnaire et interrompu : les deux règles corrigées ces deux derniers jours
ne tenaient donc qu'aux tests Python, et le portage JavaScript ne leur était
comparé sur rien. `fonctionnaire_interrompu` et `carriere_longue_hachee` ferment
ce trou, et leur diff est le premier contrôle du portage.

**Ce qui reste, et c'est écrit.** Le 6° du I — majoration du compte professionnel
de prévention — n'est pas calculé par le modèle ; la part du 7° qui vise les
fonctionnaires affiliés à un régime spécial n'est pas distinguée. Et une lecture
manque : D. 351-1-3 pose la condition de DÉBUT d'activité sur une « durée
d'assurance » de cinq trimestres quand le modèle n'y compte que les trimestres
cotisés. Le texte est plus large que le modèle ; la doctrine Cnav ne l'est
peut-être pas, et `legislation.cnav.fr` n'est pas joignable depuis une session du
dépôt. La condition reste donc plus dure que la lettre du décret, et le registre
porte la question.

**Fichiers.** `data/reference/legislation/periodes_non_travaillees.csv`,
`src/retraite_notionnelle/donnees/chargement.py`,
`src/retraite_notionnelle/carriere.py`,
`src/retraite_notionnelle/scenarios/actuel.py`, `moteur/js/carriere.js`,
`moteur/js/regimes.js`, `scripts/construire_donnees.py`,
`scripts/construire_temoins.py`, `tests/test_simulateur.py`,
`data/reference/legislation/veille.yaml`, `docs/methodologie.md`,
`docs/limites.md`.

### 93. Deux pensions là où la caisse n'en sert qu'une — `fait`

**Demande.** « Fait des recherches complémentaires et corrige », après que
l'action précédente eut laissé la liquidation unique des régimes alignés vérifiée
par construction mais faite à moitié dans le modèle.

**La règle, et ses deux conditions opposables.** L. 173-1-2 : l'assuré qui a
relevé de plusieurs des régimes alignés reçoit, pour l'ensemble, une pension
unique servie par le dernier d'entre eux, calculée comme si la carrière s'y était
déroulée en entier. R. 173-4-4-1 pose les deux bornes que le modèle doit
opposer : le 1° réserve la règle aux assurés nés **à compter de 1953** et le 4°
aux pensions prenant effet **à compter du 1er juillet 2017** — une date au mois,
pas à l'année. La circulaire Cnav 2017/27 en donne l'application, et nomme les
cinq régimes concernés : régime général, salariés agricoles, et les trois
guichets devenus le RSI (Cancava, Organic, RSI).

**Ce que le modèle faisait.** Il liquidait chaque régime aligné pour son propre
compte. Sur une carrière moitié privée moitié agricole née en 1960, cela donnait
deux pensions — « SR 41 499 € × 88/167 » d'un côté, « SR 29 069 € × 80/167 » de
l'autre — soit **18 121 €**. La caisse en sert une : « SR 40 749 € × 167/167 »,
soit **20 629 €**. L'écart de 2 508 € ne vient pas d'un salaire de référence plus
généreux — il est plus bas que celui du régime général seul — mais du taux de
proratisation, que la réunion des carrières porte de deux fractions incomplètes à
une seule entière.

**Fait des deux côtés.** `REGIMES_ALIGNES` et une tête de succession commune
`regimes_alignes` dans `ScenarioActuel._groupes_de_succession`, qui reçoit
désormais la carrière pour lire la génération et le mois d'effet ; même chose
dans `moteur/js/scenario-actuel.js`, où la borne de juillet 2017 s'écrit
`2017 * 12 + 6` pour se comparer au rang du mois.

**Aucun témoin n'a bougé, et c'est le sujet.** La grille de cas types n'exerce
qu'un statut à la fois : la liquidation unique ne se voit que sur un
polypensionné, qu'aucun témoin ne porte. Le changement ne tenait donc à rien
avant que deux tests dédiés ne soient écrits — un en Python, un en JavaScript —
qui vérifient la réunion pour 1960, la non-réunion pour 1950, et la frontière au
mois : né en 1955, liquidant en janvier 2017 deux pensions, en septembre 2017 une
seule.

**Fichiers.** `src/retraite_notionnelle/scenarios/actuel.py`,
`moteur/js/scenario-actuel.js`, `tests/test_simulateur.py`,
`tests/js/moteur.test.js`, `data/reference/legislation/veille.yaml`,
`docs/limites.md`.

### 94. Un emploi classé n'a pas la durée de sa génération — `fait`

**Demande.** « Que peut-on faire d'autre ? », troisième chantier : les lignes du
registre de veille restées `manque`. Celle-ci était la dernière des trois, et sa
fermeture vide la colonne : plus aucune ligne du registre n'est `manque`.

**Ce que le registre disait.** `categorie_active_duree_requise` portait l'état
`manque` depuis le 17 septembre 2026, avec sa mesure : « un actif né en 1969 se
voit opposer 172 trimestres au lieu de 170 ». Le modèle opposait aux emplois
classés la durée des sédentaires — celle de leur génération —, alors que deux
textes leur en fixent une propre.

**Deux textes qui disent la même chose au mot près.** Le XXIV, B de l'article 10
de la loi du 14 avril 2023 (version LEGIARTI000053280920) pour les
fonctionnaires de l'État, et le II, B de l'article 13 du décret n° 2023-435
(version LEGIARTI000054059137, issue du décret n° 2026-344) pour la CNRACL et le
FSPOEIE. Tous deux « par dérogation à l'article L. 13 » : 169 trimestres du
1<sup>er</sup> septembre 1966 au 31 décembre 1967, 170 jusqu'au 31 mars 1970, 171
jusqu'à la fin de 1970, 172 à compter de 1971 — et les mêmes marches cinq ans
plus tard pour la super-active.

**La lecture qui a élargi le chantier, et c'est ce qu'une lecture doit faire.**
Le « a) » des deux textes renvoie, pour ceux qui naissent avant ces dates, à « la
durée applicable avant l'entrée en vigueur » de la réforme — c'est-à-dire
l'article L. 161-17-3 dans sa version du 22 janvier 2014
(LEGIARTI000028494794) : 167 trimestres pour les nés de 1958 à 1960, 168 de 1961
à 1963, 169 de 1964 à 1966. La dérogation ne commence donc pas en 1966 mais dès
1961, quatre générations que le registre ne visait pas. C'est pourquoi la table
porte des lignes intercalaires aux âges identiques : elles ne sont là que pour
couper la durée là où l'ancienne table coupait.

**Et une non-monotonie que le texte assume.** Un super-actif né en juin 1971 se
voit opposer 171 trimestres par l'ancienne table, celui qui naît en octobre 1971
seulement 169 : la dérogation nouvelle commence au 1<sup>er</sup> septembre 1971
et recommence à 169. Rien n'indique une erreur de plume, et le modèle suit la
lettre.

**Ce que la correction rend.** +1,78 % de pension à un fonctionnaire d'État de
catégorie active né en 1967 parti à soixante ans — 169 trimestres requis au lieu
de 172 —, +1,18 % à un né en 1969, +0,60 % à un né en 1962. Dans la fonction
publique la durée requise commande aussi la proratisation : le gain porte sur le
taux et sur le prorata à la fois. Sept témoins du dépôt bougent, tous des
carrières classées ; sur deux d'entre eux la pension du système actuel ne bouge
pas — 172/172 devient 170/170 —, et c'est la conversion des droits acquis des
scénarios prospectifs qui s'en trouve relevée.

**Ce qui reste.** Le C du même XXIV : la durée des fonctionnaires civils et des
militaires qui liquident avant soixante ans SANS être classés — 169 trimestres,
puis un de plus au 1<sup>er</sup> janvier 2025 et au 1<sup>er</sup> janvier 2027,
la table commune à compter de 2028. `docs/limites.md` le porte.

**Et un garde-fou qui s'est mis à refuser ce qu'il fallait mesurer.** Le coût de
chaque avantage non isolé par la cascade se mesure par retrait : on refait la
pension sans l'avantage, et l'écart est la ligne. Un garde-fou refusait le
chiffre quand le retrait déplaçait aussi la DURÉE REQUISE, parce que la
proratisation change avec elle et que l'écart ne mesure plus rien de nommable.
Il visait la jouissance militaire, dont les 160 trimestres viennent de la fiche
du régime. Il s'est mis à refuser le classement de l'emploi — qui devenait le
seul avantage dont la durée requise fait PARTIE, le texte la donnant « pour les
fonctionnaires bénéficiant, au titre de la catégorie active, d'un droit au
départ à l'âge anticipé ». Cesser de chiffrer un avantage parce qu'on vient d'en
mieux comprendre la portée aurait été le contraire du but : le garde-fou porte
désormais la liste des avantages dont la durée est l'un des effets, et la ligne
reste mesurée. Elle vaut 0,5 Md € en 2024, et la page Avantages passe de 12,8 à
12,9 Md € de pensions servies avant l'âge légal.

**Fichiers.** `data/reference/legislation/categorie_active.csv`,
`src/retraite_notionnelle/scenarios/actuel.py`,
`src/retraite_notionnelle/avantages.py`, `moteur/js/regimes.js`,
`moteur/js/scenario-actuel.js`, `scripts/construire_donnees.py`,
`tests/test_simulateur.py`, `data/reference/legislation/veille.yaml`,
`docs/limites.md`, `docs/parcours_presentation.md`.
### 95. Le plafond qui ne mord pas, et le médecin libéral du COR — `fait`

**Demande.** « Fais des recherches complémentaires pour le reste » : les deux
réserves de l'action 90 — le plafond de vingt trimestres, écrit dans certains
textes et pas dans d'autres, et le cas type libéral sans carrière antérieure.

**Le plafond n'est pas une règle de plus : c'est l'arithmétique des deux
âges.** Il est écrit là où le droit a voulu l'écrire — R. 643-7 pour les
professions libérales, R. 723-38 pour les avocats, le I de L. 14 pour la
fonction publique — et absent de R. 351-27 2° comme de R. 732-61, qui ne s'en
sont jamais souciés. La raison est mesurable dans les tables du dépôt :
**l'écart entre l'âge d'ouverture et l'âge d'annulation vaut exactement vingt
trimestres pour les générations 1930 à 1961**, puis descend à dix-huit, quinze,
treize et douze à mesure que les réformes relèvent le premier sans toucher au
second. Sur toute liquidation que le droit ouvre, le décompte par l'âge est
donc borné par construction.

**Et il ne mord nulle part.** Un balayage de treize cas types × six générations
× tous les trimestres de cinquante à soixante-huit ans produit **2 483
liquidations ouvertes**, et le plafond n'en change aucune. Il ne mordrait que
sur une liquidation antérieure à l'âge d'ouverture, que le modèle refuse depuis
l'action 87. Rien à changer dans le calcul ; la docstring, qui en faisait une
règle de « tous les régimes qui appliquent une décote », est réécrite, et deux
tests tiennent l'identité — si les âges bougent un jour, le plafond cessera
d'être invisible et quelqu'un le verra.

**Le COR publie un cas type de libéral, et le dépôt le retrouve à trois mois
près.** Le rapport annuel de juin 2026 ajoute, sous le n° 13, un médecin
généraliste conventionné de secteur 1 né en 1960 : il « peut prétendre à un
départ à 62 ans » et « atteint le taux plein à 66 ans et 9 mois ». La fiche du
dépôt, pour la même génération, donne **62,00 et 67,00**. C'est la première
confrontation du dépôt à un cas type libéral publié, et elle vaut mieux que
l'âge d'un groupe de la nomenclature ou que celui d'une caisse : les deux
nombres sont construits sous la MÊME convention — on part au taux plein — là où
l'enquête Emploi et le recueil de la CNAVPL mesurent un comportement.

**Ce qu'elle a tranché.** La fiche portait une règle à elle, « ouverture plus
deux ans », qui n'était qu'un contournement : le moteur ne savait pas opposer
de durée à une carrière tout en points, et le taux plein lui rendait donc l'âge
d'ouverture. Le défaut corrigé à l'action 87, le contournement n'avait plus de
cause, et sa constante de deux ans ne s'appuyait sur aucune source. **La fiche
est rendue à la règle ordinaire**, `taux_plein` sans décalage, et
`ecart_liquidation` n'a plus qu'un usager — le militaire, dont il porte la
durée de services. Un test le tient.

**Ce que ça a déplacé.** Le libéral part à 67 ans dans toutes les générations
au lieu de 64 puis 66. La trajectoire 2070 passe de 18,35 à 18,34 % du PIB, et
la concordance d'ensemble à l'âge conjoncturel tous régimes **s'améliore**, de
−0,07 à −0,02 an. Contre l'âge OBSERVÉ de sa caisse, la fiche passe de 1,24 an
trop tôt à 1,42 an trop tard : les deux conventions manquent la moyenne réelle
d'à peu près autant, en sens contraire, et le choix ne s'est donc pas fait sur
l'ajustement mais sur la règle.

**Trois leçons.** **Une règle qu'on n'a jamais vue agir mérite qu'on cherche
pourquoi** : le plafond n'était ni faux ni utile, il était une conséquence, et
le dire coûte deux tests là où le supposer coûtait une réserve ouverte à chaque
relecture. **Un contournement survit à sa cause** si personne ne revient le
chercher : celui-ci a tenu une journée seulement parce que la réserve était
écrite. Et **la meilleure référence est celle qui partage la convention** — le
groupe 3 de la nomenclature mesure un comportement, la caisse aussi, le cas
type du COR non, et c'est lui qui tranche.

**Ce qui reste.** Le cas type libéral n'a toujours aucune carrière antérieure,
quand la CNAVPL immatricule ses affiliés à 32,58 ans en moyenne. Seule une
carrière en deux temps — salariée puis libérale — départagerait les deux
conventions, et `CasType` ne porte qu'une affiliation : c'est un chantier, non
une retouche.

**Fichiers.** `src/retraite_notionnelle/scenarios/actuel.py`,
`src/retraite_notionnelle/castypes.py`, `moteur/js/castypes.js`,
`data/reference/legislation/veille.yaml`,
`data/reference/macro/cas_types_csp.yaml`, `tests/test_cout_age_depart.py`,
`docs/limites.md` § 5 ter, `tests/temoins/pages.json`.
**Deuxième lot dépouillé : la CNRACL, le 22 septembre 2026.** La documentation
juridique du régime (`juris-cnracl.retraites.fr`), que la Caisse des dépôts
tient pour les employeurs territoriaux et hospitaliers — elle GÈRE la CNRACL,
c'est donc une source primaire, et `scripts/veille_droit.py` la nommait déjà
parmi les sources à consulter sans que personne l'ait lue.

*Aucun écart, et c'est le résultat.* Son tableau de quarante-neuf périodes, du
19 septembre 1947 à 2026, donne la retenue de l'agent et la contribution de
l'employeur. Les deux séries du dépôt s'y accordent sur les soixante-dix-neuf
années, au centième de point près, convention de date comprise. Ce qui change
n'est donc pas un chiffre, c'est son RANG : les quarante années de contribution
employeur que le dépôt tenait d'OpenFisca au niveau `haute` passent à
`certifiee`, et cette série n'a plus une seule année de second rang.
`scripts/fetch/juris_cnracl_taux.py` récupère le tableau, la certification
`employeur_public_cnracl_gestionnaire` le verse, et
`tests/test_juris_cnracl_taux.py` le tient hors réseau, les quarante-neuf
périodes transcrites.

*Ce que la source apprend en plus.* Dix années ont vu un taux changer en cours
de route, que la convention annuelle du dépôt ne peut pas rendre — la plus
lourde est 1980, où la contribution tombe de 18 % à 6 % au 1er juillet :
l'employeur a versé cette année-là la moitié de ce que le dépôt lui compte. Le
test les nomme toutes les dix et vérifie qu'il n'y en a pas d'autres. La page
mère signale par ailleurs deux cotisations supplémentaires que le dépôt ignore
— sapeurs-pompiers professionnels et aides-soignants — et le SP-CTI, le
supplément de pension du « Ségur » hospitalier, reste entier à chiffrer.

*Un piège de manipulation, à dire une fois pour toutes.*
`verifier_donnees.py --appliquer` lancé avec un `data/brut/` incomplet fait
REDESCENDRE les lignes dont la meilleure source est absente : cinq années de
la SNCF sont ainsi passées de `certifiee` à `haute` avant d'être rendues à leur
rang par la récupération manquante. Lancer les récupérateurs d'abord, et
relire le diff du fichier de référence avant de commiter.

### 96. Un mois de septembre qui tombait à côté — `fait`

**Demande.** « Fait des recherches complémentaires et corrige. »

**DEUX SESSIONS ONT LU LE MÊME TEXTE LE MÊME JOUR, et il faut le dire.** Celle-ci
a mené la même correction que l'action 94 — la durée requise propre aux emplois
classés — jusqu'au bout, avant de découvrir au rebasage que `main` la portait
déjà, table identique et valeurs identiques. C'est le cas que la règle des zones
du `CLAUDE.md` existe pour éviter : deux sessions sur le même registre de veille
se rencontrent sur la même ligne. Le travail dupliqué a été abandonné au profit
de celui de `main`, à trois choses près, qui sont ce que cette action garde.

**La première, et c'est la seule vraie trouvaille : un mois de septembre qui
tombait à côté.** L'essai écrit pour la super-active refusait de passer, et sa
raison n'était pas dans le droit. Une génération s'écrit ici en années
décimales, et les tables écrivent le 1er septembre `1961.667` — trois décimales,
comme le veut leur convention. Huit douzièmes valent 1961,666 666… Le premier
étant plus grand que le second, la lecture en escalier rendait à l'assuré né en
SEPTEMBRE 1961 la marche d'août : **168 trimestres au lieu de 169, et un âge
d'ouverture de 62 ans au lieu de 62 ans et trois mois** — pour le mois-même que
la loi du 14 avril 2023 désigne, et pour un douzième de la génération. Le trou
valait aussi pour `1963.667` de la carrière longue, `1966.667` et `1971.667` de
la catégorie active, `1971.667` de la jouissance militaire. La génération est
désormais lue à la précision où les tables sont écrites, dans les deux moteurs.

**La deuxième : un essai qui tient l'escalier marche par marche.** L'action 94
vérifiait la durée requise sur un point ; celui-ci la vérifie sur huit, dont la
marche qui DESCEND — un super-actif né en août 1971 doit 171 trimestres, celui
de septembre 169, le texte remettant leur compteur à 169 au moment même où leur
âge commence à monter — et le contre-exemple du sédentaire, qui reste au droit
commun. C'est cet essai qui a trouvé le mois perdu.

**La troisième : 868 € qui avaient dérivé à 825 €.** Le dépliant « Pourquoi le
montant ne suffit pas à le dire » portait ce chiffre en dur, et le modèle en
donnait un autre depuis un moment. Il est corrigé, daté de sa génération, et
accompagné de celui de 1965 — 102 €, le classement abaissant désormais sa durée
requise d'un trimestre. Dit au passage dans `limites.md` et dans l'inventaire
des avantages : le contrôle d'isolement de `avantages.py` refuse maintenant ce
calcul sur les cas types dont le retrait du classement déplace la
proratisation ; il en reste assez pour que la mesure tienne, et la page continue
de chiffrer dix-huit dispositifs.

**Deux lignes à ouvrir, lues et non portées.** Le F du II de l'article 13 du
décret n° 2023-435 donne à la carrière longue de la fonction publique sa propre
durée cotisée — 167 trimestres de 1958 à 1960, 171 de 1970 à 1972 —, que le
modèle n'oppose pas encore ; et le C vise les autres départs avant soixante ans.

**Fichiers.** `src/retraite_notionnelle/carriere.py`, `moteur/js/carriere.js`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`data/reference/legislation/avantages_non_contributifs.yaml`,
`data/reference/legislation/veille.yaml`, `tests/test_simulateur.py`,
`tests/test_affirmations.py`, `data/reference/site/affirmations.yaml`,
`docs/limites.md`.
**Troisième lot dépouillé : les IEG, le 22 septembre 2026.** Les pages
« réglementation » de la CNIEG, puis l'annexe 3 du statut national lue dans
l'index LEGI. Deux confirmations et deux écarts.

*Confirmé.* La montée en charge de la décote des régimes spéciaux — rien avant
le 1er juillet 2010, un dixième du taux par an, 1,25 % en 2019, et un âge
d'annulation qui recule de seize trimestres à rien de 2010 à 2024 — est
exactement ce que le dépôt applique depuis qu'il a lu le texte de l'Opéra de
Paris. La caisse publie les deux tables à l'identique. Le taux de surcote,
1,25 % par trimestre depuis 2009, l'est aussi.

*Corrigé : sept trimestres de décote de trop, depuis 2025.* Le I de l'article 10
de l'annexe 3, dans sa version en vigueur (LEGIARTI000052046924), compte les
trimestres de minoration jusqu'à « un âge de référence correspondant à l'âge
minimum d'ouverture du droit à pension applicable à l'assuré **majoré de trois
ans** » — cinq ans avant la réforme de 2023 —, et son article 45 fixe cet âge à
soixante-deux ans pour les agents en services actifs nés avant 1975. La fiche
portait 63,75 puis 64 ans. Sur le cas type des IEG, l'écart au système actuel
passe de −23 % à −32 % pour la génération 1970 et de −38 % à −45 % pour celle
de 2000 : l'agent des IEG devient, en tête de la page Cas types, la carrière la
moins bien traitée par la proposition, à la place du militaire non officier.

*Déclaré, non corrigé : le régime a sa propre table de durée requise.* 169
trimestres pour la génération 1963, 170 pour 1964-1965, 171 pour 1966-1967, 172
à partir de 1968 — trois générations de moins que la table commune que le dépôt
lui oppose. Un trimestre vaut 1,25 % de décote ou 0,6 % de pension. Le corriger
demande une quatrième table dans `_duree_requise` — après celle de la fonction
publique, celle de la catégorie active et la table commune — et son portage
JavaScript : c'est la ligne `duree_requise_ieg` du registre de veille, état
`manque`. La CNIEG publie en outre une table par MOTIF D'ANTICIPATION, que le
dépôt ne porte pour aucun régime spécial.

*Et la question qu'il laisse ouverte.* La SNCF et la RATP portent la même
construction — âge d'ouverture majoré de cinq ans — et leurs textes n'ont pas
été lus. Si la réforme de 2023 les a traitées comme les IEG, deux autres fiches
décotent de trop. C'est la première chose à faire du prochain lot.

**Quatrième lot dépouillé : la SNCF et la RATP, le 22 septembre 2026.** La
question que les IEG laissaient ouverte avait la réponse attendue, et deux de
plus. Les textes lus dans l'index LEGI à jour de l'incrément du 21 : les
articles 13, 15, 35 et 37-1 du décret n° 2008-639, les articles 6, 24, 51 et
51-1 du décret n° 2008-637, chacun dans toutes ses versions ; chez les
caisses, trois pages de la CPRPSNCF, et les pages publiques de la CRP RATP,
qui ne publient rien de la décote.

*Corrigé : l'âge de référence de la décote ne monte pas.* Le 1° du I de
l'article 13 du décret de la SNCF le FIXE depuis le décret du 20 octobre 2023
à cinquante-sept ans pour les agents de conduite, soixante-deux pour les
autres ; celui de la RATP le fixe à l'âge d'ouverture FINAL majoré de trois
ans, cinquante-sept ans au tableau B, et garde de 2025 à 2033 l'âge d'avant,
qui vaut aussi cinquante-sept. Les deux fiches le faisaient monter jusqu'à
cinquante-neuf ans, et prenaient pour l'âge d'annulation les soixante-deux à
soixante-quatre ans des générations 1963 à 1970, qui sont ceux de la surcote.
La CPRPSNCF l'écrit : « L'âge d'annulation de la décote est inchangé ». Un
agent de conduite né en 1980 parti à cinquante-quatre ans passe de vingt
trimestres de décote à douze, de 56,25 % à 63,75 %, de 23 711 € à 26 872 € ;
le même à la RATP.

*Corrigé : chacun a sa table de durée requise, et la suspension ne la touche
pas.* 170 trimestres pour un agent de conduite né en 1975, non 172 ; 171 pour
un agent de la RATP né en 1966, non 172. L'article 105 de la loi du
30 décembre 2025 ne réécrit que le code de la sécurité sociale et la loi de
2023 pour la fonction publique, et aucun décret n'a repris la suspension dans
ces deux régimes : `reformes.yaml` le déclare. La SNCF compte en outre la
décote par la durée sur une cible abaissée de deux à dix trimestres (II de
l'article 35). C'est la quatrième table de `_duree_requise`, que la ligne
`duree_requise_ieg` demandait : `legislation/duree_requise_regimes_speciaux.csv`,
le champ `duree_requise_table` des fiches, et son portage.

*Corrigé en chemin : la surcote partait de l'âge d'ouverture.* Les deux décrets
ne la comptent qu'au-delà d'un âge propre, soixante-quatre ans à compter de la
génération 1970 ; le modèle partait de cinquante-quatre. Invisible tant que la
durée requise était de 172 trimestres, le défaut est apparu sur le témoin de
l'agent SNCF, qui recevait deux trimestres de surcote qu'il n'avait pas
accomplis (`legislation/age_surcote_regimes_speciaux.csv`).

*Ce que ça déplace.* Le cas type « Agent de conduite SNCF » passe, dans les
deux dernières générations de la page Cas types, de −17 % à −25 % et de −26 %
à −34 % : c'est sa pension ACTUELLE qui remonte. Les agrégats de la page Coût
bougent d'un dixième. Trois témoins nouveaux tiennent les trois branches dans
les deux moteurs.

*Et ce que le lot défait.* Aux IEG, la table qu'on croyait devoir brancher
est celle des sédentaires ; l'agent actif du cas type relève du I bis de
l'article 45, quatre tables selon ses années de services actifs, que le
dépôt ne sait pas choisir. Restent aussi la table des agents sédentaires de
la SNCF, qu'aucune fiche ne modélise, et les carrières longues des deux
régimes.

**Les IEG, le lendemain : la table des dix-sept ans.** Le I bis de l'article
45 n'a pas quatre tables mais cinq, une par seuil de services actifs — cinq,
huit, onze, quatorze et dix-sept ans, les mêmes qui abaissent l'âge
d'ouverture d'un à cinq ans. Le choix, que le dépôt « ne savait pas faire »,
est fait par la fiche elle-même : elle ouvre le droit à l'âge légal abaissé
de cinq ans, c'est-à-dire aux dix-sept ans, et lit leur table
(`ieg_actif_17`). En deçà de la génération 1968, le texte renvoie à la durée
d'avant le décret n° 2023-692, qui n'est pas la table actuelle du I mais
celle de 2014, lue dans la version de 2020. Un agent né en 1968 doit 170
trimestres, la table commune lui en demandait 172. Les quatre autres tables
sont transcrites sans lecteur : il faudrait compter les années actives de la
carrière. Et l'âge d'ouverture de la fiche n'a pas été confronté à la
suspension de 2026 — c'est la question que ce lot laisse.

### 97. Quel salaire faut-il rentrer ? Celui du travail, et jamais la pension — `fait`

**Demande.** « Sur le simulateur, il faut rentrer quel salaire ? Moi je rentre
mon salaire actuel, mais un retraité veut rentrer sa retraite actuelle. J'ai
l'impression que ce n'est pas si clair que ça. »

**Le champ demandait « Revenu net mensuel », et la date de départ juste
au-dessus peut être passée.** Les deux ensemble se lisent « ce que vous touchez
aujourd'hui ». Un actif y met son salaire, ce qui est la bonne réponse ; un
retraité y mettrait sa pension, et **rien ne clocherait** : le modèle
cotiserait sur ce montant comme sur un salaire, et rendrait une pension bien
plus petite que celle qu'il touche déjà. Un résultat faux, vraisemblable, et
que personne ne peut détecter à l'œil — le pire des trois.

**Le libellé porte maintenant le mot qui tranche : « Revenu d'activité net
mensuel », « Niveau de revenu d'activité ».** Il se lit sans rien ouvrir, et
c'est le terme du droit : un revenu d'activité n'est pas un revenu de
remplacement. Le complément du champ dit ensuite ce qu'un retraité doit saisir
à la place — ce qu'il gagnait en travaillant, **au milieu de sa carrière**,
puisque c'est le point sur lequel le profil de carrière est centré —, et le
renvoie au dépôt du relevé, qui écrit la carrière année par année et dispense
de l'estimer. La phrase est commune aux quatre compléments du champ : la
confusion ne tient ni au mode d'affichage, ni au statut, ni à l'unité de
saisie.

**Reste à décider, et non fait : saisir sa pension POUR DE BON.** Un retraité
connaît son montant au centime ; le simulateur, lui, lui demande d'estimer un
salaire d'il y a trente ans. Inverser le scénario 1 — chercher le niveau de
revenu dont il tire la pension observée, par dichotomie sur un calcul qui est
monotone en ce niveau — donnerait une carrière calibrée sur un chiffre connu,
et les trois autres systèmes se calculeraient dessus. C'est une fonctionnalité,
pas une clarification : elle change ce que le simulateur affirme, et demande sa
propre action.

**Le premier jet a été poussé rouge, et le cliquet des incises l'a dit.** Le
hook `Stop` de l'action 36 pousse à la fin du tour, et il a poussé pendant que
la suite tournait encore : `main` a porté quelques minutes un texte dont les
deux incises en tiret cadratin faisaient passer `/simuler` de quatorze phrases
à seize, au-dessus du plafond que `test_les_incises_en_tiret_restent_rares`
tient. Le complément a été réécrit en deux-points et en phrases séparées, ce
qui vaut mieux de toute façon. **La leçon est sur l'ordre des gestes, pas sur
le hook** : quand la suite complète met neuf minutes, le commit doit attendre
qu'elle soit verte, puisque le commit vaut publication.

**Fichiers.** `src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`tests/test_web.py`, `tests/temoins/pages.json`, `README.md`.

### 98. Ce qui bloquait n'était pas le conteneur : cinq adresses mortes — `fait`

**Demande.** « Regarde dans le projet tous les sites qui bloquaient à cause de
l'environnement Cloud. J'utilise une session locale qui pourrait débloquer la
plupart de ces blocages. »

**Le diagnostic.** La liste existait — l'action 45 l'avait faite, et
`python scripts/fetch/source_locale.py` l'imprime —, mais elle mélangeait deux
choses sous le mot `reseau` : les hôtes qu'un environnement de construction ne
joint pas, et les hôtes que PERSONNE ne joint plus. Les dix jeux bloqués du
manifeste et les hôtes que `limites.md`, `exploration_sources.md` et ce
document-ci tenaient pour hors d'atteinte ont été sondés un à un depuis un
poste ordinaire, le 22 septembre 2026, en requête simple puis dans un
navigateur pour ceux qui opposent un défi anti-robot.

**Cinq noms d'hôte sont morts, trois ont un successeur.** C'est le vrai
résultat, et il ne demandait aucun poste particulier : il demandait qu'on
distingue « la machine ne joint pas » de « l'adresse n'existe plus ».

| Écrit dans le dépôt | En réalité |
|---|---|
| `legislation.cnav.fr` injoignable | `legislation.lassuranceretraite.fr`, que `scripts/fetch/cnav_revalorisation_salaires.py` interrogeait DÉJÀ |
| `statistiques-recherches.cnav.fr` | `statistiques-recherche.lassuranceretraite.fr`, au singulier, que le jeu voisin citait déjà |
| `www.cprpsncf.fr` injoignable | `www.cprpf.fr` — le serveur le disait, son certificat portant déjà ce nom |
| `opendata.sncf.com` injoignable | `data.sncf.com` |
| `epsilon.insee.fr`, `performance-publique.budget.gouv.fr` | morts, sans successeur trouvé |

Deux passages de ce document restent donc écrits tels quels, et faux pour la
raison qu'ils donnent : le « `legislation.cnav.fr` n'est pas joignable depuis
une session du dépôt » de l'action 92, et les « injoignables depuis ce
conteneur » de l'action 37. Ils sont `recit`, vrais à leur date ; c'est le
manifeste qui porte désormais l'adresse juste, et la circulaire Cnav 2026-29
que la première disait hors d'atteinte est à portée.

**Ce qu'un poste apporte vraiment, et ce qu'il n'apportait pas.** La Cour des
comptes est le seul gain : `ccomptes.fr` ferme la connexion depuis une session
et répond 200 depuis un poste. Le rapport sur les droits de succession —
92 pages — est apporté, avec les dix-huit CSV de ses graphiques que la Cour
publie à côté. C'est ce que l'action 47 attend pour la reprise de la garantie
vieillesse : le dépôt mesure aujourd'hui la couverture d'une avance sur le
patrimoine des MÉNAGES retraités, jamais sur ce que les successions portent
réellement. Pour le reste, rien de neuf : `budget.gouv.fr` s'ouvre au
navigateur, mais ses trois annexes ont un miroir à l'Assemblée nationale depuis
l'action 45 et `--recuperer` les rapporte sans personne ; la Banque de France,
qui refusait la session ET le runner, répond 200 ici, mais `OPEF2026.pdf` est
déposé sur la release depuis le 20 septembre ; Légifrance refuse encore la
requête simple et s'ouvre au navigateur, quand l'index LEGI du dépôt sert déjà
le même contenu. `drees_eic` et l'enquête Patrimoine sont sous convention :
aucun poste ne les débloque.

**Ce qui n'est pas fait.** Le rapport de la Cour n'a pas de lecteur : ses
valeurs ne sont pas entrées dans le dépôt, et `cdc_successions_2024` reste
`a_faire`. `data/brut/` n'est pas versionné — le document sert à la session qui
l'a déposé, et c'est le lecteur, versionné, qui rendra la valeur
recontrôlable. Le blocage du jeu reste `reseau` : un poste le joint, une
session non.

**Fichiers.** `data/sources.yaml` (quatre jeux : deux adresses corrigées, le
document de la Cour déclaré avec son empreinte, deux notes),
`data/reference/legislation/veille.yaml` (journal du 22 septembre 2026).

### 99. Saisir sa pension plutôt que son salaire : le scénario 1 s'inverse — `fait`

**Demande.** « Je veux qu'on puisse avoir le choix de rentrer soit la pension
soit le salaire. »

**Pourquoi c'était la bonne demande.** L'action 97 avait clarifié le champ de
revenu : elle disait à un retraité de ne pas y mettre sa pension, et de saisir
à la place ce qu'il gagnait trente ans plus tôt. C'est une réponse honnête à
une mauvaise question. Le retraité connaît sa pension au centime ; le revenu,
il l'estime. Le simulateur, lui, sait calculer — et ce qu'on lui demandait
d'estimer est précisément ce qu'il sait faire, dans l'autre sens.

**Le formulaire a une troisième bascule : « Je saisis — mon revenu d'activité /
ma pension ».** En mode pension, les champs de revenu de chaque période
disparaissent — ce sont eux que la page cherche —, un champ de pension les
remplace, et l'unité de saisie s'efface avec eux puisqu'elle ne gouverne plus
aucun nombre. La page de résultats ouvre alors sur le revenu trouvé, avant les
quatre montants : c'est la question qu'on a posée.

**AUCUNE DONNÉE NOUVELLE À CERTIFIER, et c'est le point qui décidait de la
faisabilité.** Le moteur ne calcule qu'une pension au moment de la liquidation :
jamais celle qu'un retraité touche aujourd'hui. Remonter de l'une à l'autre
aurait demandé la série des revalorisations réellement servies, à lire dans les
arrêtés — un chantier de veille à lui seul. Il se trouve qu'il n'y en a pas
besoin : la page exprime cette première pension **en euros constants de l'année
de référence**, et le droit indexe les pensions servies sur les prix. Une
pension qui a suivi les prix garde son pouvoir d'achat : la somme qu'un retraité
touche aujourd'hui EST sa première pension exprimée en euros d'aujourd'hui. La
cible saisie et le montant calculé sont donc déjà dans la même unité. Les
sous-indexations décidées certaines années font seules la différence, et le
champ le dit.

**L'inversion est une dichotomie de dix-huit coupes sur le scénario 1** — le
droit en vigueur, seul des quatre systèmes qu'il ait un sens d'inverser,
puisque c'est le seul que l'assuré a réellement subi. Dix-huit coupes sur
[0,1 ; 10] laissent treize centimes de revenu mensuel. Le compte de tours est
FIXE et non un arrêt sur convergence : les deux moteurs doivent rendre le même
niveau au bit près, et c'est la seule boucle du site dont le résultat dépende
de l'ordre des opérations flottantes. Vingt évaluations du scénario 1 : 115 ms
dans le navigateur, où une évaluation coûte 7 ms — contre 200 ms en Python, qui
ne sert ici qu'aux tests.

**La dichotomie cherche une BORNE, pas une racine, et c'est ce qui rend les
refus possibles.** La pension n'est pas une fonction bijective du revenu, et
les trois cas où elle ne l'est pas sont le droit :

- **elle plafonne** — au-delà du plafond de la tranche la plus haute du statut,
  cotiser davantage n'acquiert plus rien, et toutes les carrières mieux payées
  servent la même pension ;
- **elle a un plancher** — le minimum contributif et l'ASPA servent un montant
  qu'aucun revenu ne fait descendre ;
- **elle SAUTE**, et c'est la trouvaille de l'action. Une année ne valide quatre
  trimestres qu'à partir de 150 heures de SMIC ; au-dessous, la carrière compte
  pour moins qu'elle n'a duré, le minimum contributif est proratisé d'autant, et
  la pension bondit au franchissement du seuil. Sur un salarié du privé né en
  1955, parti à 62 ans après une carrière complète, **aucun revenu ne donne de
  pension entre 401 € et 816 € bruts par mois** — en euros de son année de
  départ, 2017, qui est l'unité dans laquelle le moteur calcule. Chercher une racine aurait rendu,
  dans ce cas, un revenu dont la pension n'est pas celle qu'on demandait, sans
  que rien ne le signale — le pire des trois résultats. La dichotomie converge
  vers le bord du saut, la pension rendue est celle d'après, et l'écart à la
  cible est ce qui fait le refus. Le refus nomme les deux bords du trou.

**Ce que l'inversion suppose, et qui est vérifié.** La pension doit être
croissante en le revenu : cotiser plus n'a jamais acquis moins. Rien dans le
code ne l'impose, et une règle ajoutée un jour pourrait le démentir sans
qu'aucun autre test ne bronche. `test_la_pension_ne_decroit_jamais_quand_le_revenu_monte`
balaie donc trente niveaux sur cinq statuts, un par famille de plafonds.

**Une convention, dite en toutes lettres sous le champ :** toutes les périodes
reçoivent le même niveau de revenu, que le profil de carrière déforme ensuite.
Inverser une pension ne donne qu'un nombre, et une carrière en compte autant
qu'elle a de métiers ; pour un revenu par métier, c'est le relevé qu'il faut
déposer. Le lien « reprendre cette carrière en saisissant le revenu », sous le
chiffre trouvé, fait le passage sans rien perdre — c'est le seul endroit où la
bascule traduit, la bascule du formulaire ne le pouvant pas faute de connaître
le résultat d'un calcul qui n'a pas eu lieu.

**Fichiers.** `src/retraite_notionnelle/simulateur.py`, `moteur/js/simulateur.js`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`src/retraite_notionnelle/web/gabarit.py`, `scripts/construire_temoins.py`,
`tests/test_simulateur.py`, `tests/test_web.py`, `tests/temoins/pages.json`.

### 100. Le calculateur de la caisse corrige le dépôt : un coefficient de fusion faux — `fait`

**Demande.** « Est-ce qu'il y a encore des sites qui étaient bloqués dans
l'environnement cloud de Claude Code qui peuvent être débloqués par une
session locale ? » Puis : « fais les 2 » — corriger l'inventaire, et
dépouiller un simulateur.

**Les huit sources, et ce qui les ouvre.** `data/sources_a_explorer.yaml`
porte 260 adresses dont huit demandaient un geste. Sondées depuis un poste
ordinaire : six répondent 200 en simple requête, deux passent au navigateur
(Cloudflare pour la CRP RATP, Légifrance). Mais le mérite n'est pas au lieu.
Pour les trois `chaine_incomplete`, ce qui change est le CLIENT : le serveur
omet l'intermédiaire de son certificat, et un client qui va le chercher par
l'extension AIA — tout navigateur, et le `curl` de Windows adossé à Schannel
— le rattrape seul, vérification entière. Pour les deux `git`, `git clone`
passait déjà. Pour Légifrance, l'index LEGI du dépôt sert le même contenu.

**Et une ligne `ferme` qui ne l'était plus.** Le calculateur Agirc-Arrco était
classé hors de portée pour certificat EXPIRÉ — constat juste, et
infranchissable. Or le certificat a été renouvelé le jour même : émis le
22 septembre 2026, valable jusqu'au 8 avril 2027. La session qui l'avait
sondé l'a attrapé dans la fenêtre du renouvellement. Plus aucun jeu de
l'inventaire n'est `ferme`.

**Ce que le calculateur a rendu, et c'est une correction du dépôt.** `calcru`
n'est pas un simulateur de pension : il convertit des points d'avant 2019 en
points Agirc-Arrco. C'est donc l'oracle du coefficient de fusion — et il a
levé une erreur que personne ne relisait.

| | Coefficient Agirc → Agirc-Arrco |
|---|---|
| `conversions_points.csv` | 0,347798289 |
| Son propre commentaire | « le rapport 0,4378 ÷ 1,2588 » |
| Ce rapport vaut | **0,347791548** |
| Le calculateur de la caisse affiche | **0,347791548** |

Le fichier se contredisait : le nombre enregistré n'était pas le quotient que
sa note prescrivait. L'exemple publié par la caisse tranche — 1 000 points
Agirc valent 437,80 €, ce que le quotient rend à l'euro près et que
l'ancienne valeur manquait de 8 millièmes. L'écart relatif est de
1,9 × 10⁻⁵ : il déplace 2 448 valeurs de témoins, toutes des pensions
complémentaires du scénario 1, et l'écart maximal mesuré sur les témoins est
exactement celui du coefficient — la correction ne fait rien d'autre.

**Le garde-fou, qui est le vrai résultat.** L'erreur a vécu parce que RIEN NE
RECALCULAIT le nombre, alors que ses deux bornes sont dans le dépôt,
certifiées : les valeurs de service Agirc et Arrco de 2018.
`test_les_coefficients_de_fusion_se_recalculent_depuis_les_valeurs_de_point`
refait le quotient et vérifie l'exemple de la caisse ; vérifié qu'il rejette
bien l'ancienne valeur. Un changement d'unité n'est pas un nombre à recopier.

**Ce qui reste.** Les trois parcours du GIP Union Retraite (liste des
simulateurs, retraite progressive, expatriation) sont joignables et non
dépouillés — l'expatriation vise une limite que `docs/limites.md` déclare
hors modèle. Et l'en-tête de `tests/temoins/exemples_officiels.yaml` affirme
encore qu'« aucun simulateur officiel n'est automatisable », ce que l'action
89 a démenti : à reprendre avec le premier oracle qui donnera une pension.

**Fichiers.** `data/reference/regimes/conversions_points.csv`,
`data/sources_a_explorer.yaml`, `tests/test_donnees.py`, et les fichiers
fabriqués : `moteur/donnees.json`, `data/derive/equilibre.json`,
`tests/temoins/simulations.json`, `tests/temoins/pages.json`.


### 101. Dix-huit tests rouges sur Windows, et aucun n'accusait Windows — `fait`

**Demande.** « Corrige et reprends tout ce qui ne va pas. »

**Le diagnostic.** Une machine Windows faisait échouer dix-huit tests que
Linux passait. La tentation était de les mettre au compte de la plateforme :
trois défauts du DÉPÔT s'y cachaient, qu'aucune session Linux ne pouvait
voir, et le troisième écrivait des chiffres faux dans le README.

**`tar` et la lettre de lecteur — douze tests.** `tar` lit un argument qui
contient un deux-points comme `hôte:chemin`, et un chemin absolu de Windows
commence par `C:`. GNU tar répondait « Cannot connect to C: resolve failed »,
`dila_index` construisait un index VIDE, et rien ne le disait — l'échec
arrivait douze tests plus loin, sous la forme d'un ensemble vide. Le nom nu
depuis le répertoire de l'archive (`cwd=archive.parent`) ne demande rien à
personne ; `--force-local` aurait marché aussi, mais c'est une option GNU que
le tar BSD de Windows n'a pas.

**L'encodage, dans les deux sens — cinq tests.** Vingt-six
`subprocess.run(text=True)` décodaient avec l'encodage de la plateforme,
cp1252 ici : toute sortie accentuée revenait en mojibake, d'où les échecs du
portage JavaScript, de la coquille et du glossaire. Ils décodent maintenant
en UTF-8, explicitement. Mais la réciproque est le vrai piège, et elle a
mordu pendant la correction : **forcer la LECTURE en UTF-8 ne suffit pas si
l'enfant ÉCRIT en cp1252.** Un `pytest --collect-only` imprime des
identifiants accentués ; le décodage échouait dans le fil de lecture,
`stdout` revenait à `None`, et la sonde `tests()` cessait de répondre. Les
dix-sept sous-processus Python du dépôt tournent donc en mode UTF-8
(`-X utf8`). Une correction à un seul bout aurait remplacé un échec par un
autre — c'est ce qui s'est passé, le temps d'un test.

**Le CRLF, et ce n'était pas qu'un test rouge.** L'installeur de Git for
Windows pose `core.autocrlf=true` dans la configuration SYSTÈME : tout clone
Windows reçoit un répertoire de travail en CRLF sans que personne l'ait
demandé. Le dépôt stocke des LF, et ce sont ces octets que l'hébergeur sert.
L'écart ne se voyait pas jusqu'à ce qu'on mesure : la sonde `poids` compte
les octets SUR LE DISQUE, et rendait 4 626 Ko là où le site en sert 4 594.
Or `verifier_prose.py --corriger` écrit ce qu'il mesure : **il a inscrit ce
chiffre faux dans le README deux fois dans la session, rattrapé à la main les
deux fois.** Un `* text=auto eol=lf` dans `.gitattributes` prime sur
`core.autocrlf` quelle que soit sa portée : la règle appartient au dépôt,
aucune machine n'a à être reconfigurée, et le dépôt n'a rien changé de son
contenu — il stockait déjà des LF, seul le disque mentait.

**Et une affirmation devenue fausse.** L'en-tête de
`tests/temoins/exemples_officiels.yaml` écrivait qu'« aucun simulateur
officiel n'est automatisable ». C'est vrai des simulateurs NOMINATIFS, qui
exigent FranceConnect, et faux des vingt-huit calculettes anonymes que
l'action 89 recense — dont l'une vient de corriger le dépôt (action 100).
La phrase est reprise et dit maintenant ce qu'elle voulait dire.

**Le résultat.** `python -m pytest` : **2 070 passés, 1 ignoré, zéro échec**,
et `verifier_prose.py` dit le vrai sans qu'un seul chiffre ait eu à être
réécrit. La suite tient en seize minutes sur cette machine, là où
`CLAUDE.md` en annonce trente-cinq secondes : c'est le coût du démarrage de
processus sous Windows, et il n'est pas traité ici.

**Fichiers.** `.gitattributes`, `scripts/fetch/dila_index.py`, les treize
autres récupérateurs DILA, `scripts/verifier_prose.py`,
`tests/test_pousser.py`, `tests/test_prose.py`, `tests/test_releve_lu.py`,
`tests/test_web.py`, `tests/temoins/exemples_officiels.yaml`.

### 102. Deux revenus sur le même écran, et une bascule qui changeait la carrière — `fait`

**Demande.** « Il y a des infos contradictoires dans les résultats. Le nouveau
résultat retraite est en contradiction avec les scénarios. »

**C'était vrai, et deux fois.**

**PREMIÈRE CONTRADICTION : DEUX REVENUS À QUELQUES CENTIMÈTRES L'UN DE
L'AUTRE.** Le bloc de l'action 99 annonce « le revenu que votre pension
suppose : 2 089 € nets par mois » ; la barre du système actuel, juste
au-dessous, porte « salaire 2 289,24 € net/mois ». Les deux sont justes et ne
disent pas la même chose : le premier est le niveau du MILIEU de carrière —
celui que le formulaire demande, et que le profil déforme ensuite —, le second
est ce que cette carrière paie l'année de référence des fiches de paie, où
l'assuré a cinquante et un ans. Le profil de carrière fait monter le revenu
avec l'âge : l'écart est la pente, pas une erreur.

L'ambiguïté PRÉEXISTAIT — en saisie par le revenu, on tape déjà un nombre que
les barres ne redisent pas — mais elle ne se voyait pas : il fallait comparer
ce qu'on avait tapé à ce qu'on lisait. Le bloc du revenu déduit a mis les deux
chiffres côte à côte, et une ambiguïté qui se voit est une contradiction. Le
bloc nomme donc le second revenu, dit de quelle année il est et pourquoi il est
plus haut. La phrase se tait dans les deux cas où elle n'aurait rien à dire :
quand les barres ne portent pas de salaire — un retraité ne cotise plus — et
quand le profil est plat, les deux nombres tombant alors sur le même euro.

**SECONDE CONTRADICTION, ET C'EST UN VRAI BOGUE : la bascule net/brut ne
traduisait pas la pension saisie.** Elle traduit les salaires depuis toujours,
et pour une raison écrite dans son propre commentaire : le nombre du formulaire
est un net en mode net, et le recopier tel quel dans l'autre mode le ferait
relire comme un brut. La pension avait rouvert exactement ce trou. Taper
1 800 € nets, cliquer sur « brut », et la page relisait 1 800 € BRUTS — une
pension plus petite d'un dixième, donc une autre carrière, donc un autre revenu
déduit, sans un mot. Elle porte maintenant 1 980 €, et le taux appliqué est
celui des pensions : une pension ne supporte que la CSG, la CRDS et la CASA.

**Deux tests, un par bogue**, et le second vérifie aussi que la phrase se tait
sous un profil plat — sans quoi elle expliquerait une différence qui n'existe
pas.

**Fichiers.** `src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`tests/test_web.py`, `tests/temoins/pages.json`.

### 103. La première question n'était pas la bonne : en activité, ou à la retraite ? — `fait`

**Demande.** « Je pense que la première des questions serait de demander si la
personne est en retraite ou en période d'activité. Ce serait beaucoup plus
simple dans l'expérience utilisateur. »

**La bascule de l'action 99 posait une question de modélisation déguisée.**
« Je saisis : mon revenu / ma pension » demande de choisir une ENTRÉE DU CALCUL
à quelqu'un qui n'est pas venu modéliser. Or ce choix se déduit : un actif ne
connaît pas sa pension, un retraité ne se souvient pas de son salaire. La
question a donc été remplacée par celle qui la rend inutile — **« Vous êtes :
en activité / à la retraite »** —, et elle est posée AVANT le premier champ,
parce qu'elle commande tout le reste. Son lien porte les deux réglages : un
clic reconfigure le formulaire d'un coup.

**Elle n'entre dans aucun calcul, et c'est ce qui la rend sûre.** Le modèle ne
lit que la DATE DE DÉPART, qui dit au mois près si la pension est déjà servie.
La situation n'oriente que le formulaire : ce qu'il demande, et comment il le
nomme — la date de départ dit maintenant « effectif » ou « souhaité », et non
plus les deux. Deux réglages qui se contrediraient ne peuvent donc fausser
aucun chiffre, et le cas se produit au premier clic : l'exemple par défaut est
celui d'un actif né en 1975, et le déclarer retraité laisse son départ en 2039.
**Le formulaire le dit au lieu de le corriger** : réécrire deux dates sous les
doigts de quelqu'un effacerait une carrière saisie, et refuser l'arrêterait sur
un réglage qui ne change aucun résultat.

**L'échappatoire est offerte dans un sens seulement, et c'est un arbitrage
assumé.** Un retraité qui a gardé ses fiches de paie peut donner son revenu :
une ligne sous le champ, et non une bascule permanente qui aurait remis à tout
le monde la question qu'on venait de retirer. Le chemin inverse — un actif qui
vise une pension — existe, la page le calcule et le complément du champ le
dit ; mais c'est une autre question que celle du simulateur, elle n'intéresse
qu'une minorité, et une ligne de plus sur le formulaire de TOUT LE MONDE est un
prix trop élevé pour elle.

**Le compte de mots du formulaire redescend sous ce qu'il valait avant
l'action 99** : 162 au lieu de 163, et de 160 avant les deux. Une bascule
remplacée par une bascule, une aide de trois mots ramenée à un — la question de
l'utilisateur a rendu le formulaire plus court, pas seulement plus clair, et le
cliquet du test a été resserré d'autant.

**Fichiers.** `src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`scripts/construire_temoins.py`, `tests/test_web.py`,
`tests/temoins/pages.json`.

### 104. Le chiffrage budgétaire pour un PLF : deux variantes, et quatre arbitrages que le programme ne tranche pas — `fait`

**Demande.** Rassembler les projections de dépenses et de recettes de la
proposition, pondération du recensement comprise, en un tableau annuel lisible
pour un projet de loi de finances, et signaler les hypothèses encore fragiles.

**Rien n'était à calculer : tout était à rassembler.** `cout.calculer_cout`
portait déjà chaque grandeur, mais dans deux objets qui ne parlent pas la même
unité — `Solde` en parts de PIB, avec un PIB mis à zéro hors de la fenêtre
publiée, `Avenir` avec la garantie, les reprises et un PIB nominal projeté. Le
chiffrage les réunit année par année, de la bascule à 2070, en points de PIB
et en milliards d'euros courants, et dit dans ses conventions que les euros
lointains portent une hypothèse de croissance.

**Deux variantes et non une, parce que leur écart est le premier fait
budgétaire du dossier.** La rétroactive, défaut du dépôt, recalcule les pensions
déjà liquidées ; la prospective, empruntée à `proposition_prospective.py`, fige
les droits acquis. La seconde dégrade le solde de 3,6 points de PIB de plus
l'année de la bascule. Un PLF ne peut chiffrer que celle-là, sauf à assumer
une loi rétroactive.

**Le résultat qui organise le document : la proposition retire plus de
recettes que de dépense.** En 2026, 6,1 points de recettes contre 4,8 de
dépense, pensions et garantie comprises ; le solde public se dégrade de
1,34 point, alors même que la dépense de pensions baisse de plus d'un tiers.

**Quatre arbitrages ouverts, dont deux plus lourds que cet écart.** Les impôts et
taxes affectés sortent du compte de la retraite, mais le programme ne dit pas
si l'État cesse de les lever : 2,14 points en 2026, et le signe de la lecture
en dépend. Les subventions d'équilibre posent la même question en plus petit.
La rétroactivité. Et le coefficient d'équilibre, calculé à 0,89 et jamais
appliqué — le déficit affiché et la baisse de pension qu'un pilotage
imposerait sont deux lectures du même manque, qui ne s'additionnent pas.

**Une trouvaille en chemin, laissée telle quelle.** Deux paragraphes de
`limites.md` (« Le scénario 6, et ce que sa garantie ne voit pas ») portent
encore la garantie d'avant la pondération du recensement — 1,30 % du PIB en
2026 et 20,7 milliards en 2024, quand le modèle en donne 0,58 % et 17,4. Ils
sont en zone `recit`, ce qui est leur régime voulu, et le contrôle de fraîcheur
passe à juste titre. Le chiffrage le signale pour qu'ils ne soient pas cités
dans un document budgétaire. Et `Avenir.cumul` commence à la première année
PROJETÉE, un an avant la bascule : le « 729 de 2026 à 2070 » de la même section
est en réalité 2025-2070. Le chiffrage somme sur la seule fenêtre qu'il annonce.

**Tous les chiffres sont produits, la prose seule est datée.** Le document
est `recit` dans `zones.yaml` — il raconte ce que ces tableaux voulaient dire
le 22 septembre 2026 —, mais chacun de ses huit tableaux est un bloc que
`scripts/chiffrage_plf.py` réécrit, et `test_le_chiffrage_plf_n_est_pas_perime`
refuse un document ou une série qui ne seraient plus les siens. La prose
renvoie aux tableaux plutôt que de recopier leurs chiffres. Le test coûte deux
`calculer_cout`, une trentaine de secondes, que xdist absorbe.

**Fichiers.** `scripts/chiffrage_plf.py`, `docs/chiffrage_plf.md`,
`docs/chiffrage_plf.csv`, `data/reference/prose/zones.yaml`,
`tests/test_prose.py`, `README.md`, `CLAUDE.md`, `docs/limites.md` (compte de
tests).

### 105. Six comptes faux dans `limites.md` — `fait`

**Demande.** Corriger les erreurs relevées en résumant `limites.md` section par
section, le 22 septembre 2026.

**Six comptes que la prose annonçait et que le dépôt dément.** « Dix erreurs de
calcul » en listait onze. Les « vingt-cinq entrées » de ce qui reste hors de
portée, au §1, sont vingt-huit, et le partage qui les suit en comptait
vingt-trois : seize sont refermées par une source, non douze, et le minimum
vieillesse en occupe deux. Les « cinquante-huit profils » d'OpenFisca sont
quarante-huit (10 + 10 + 7 + 10 + 11), et ils l'étaient déjà le jour où la
phrase a été écrite ; le README, qui portait le même nombre, a été ancré le même
soir par une autre session. Les exemples officiels sont trente, et non
vingt-huit : les deux de l'ENIM, entrés le matin même (action 89), manquaient au
tableau du §3, qui les porte désormais. La LURA, servie depuis le 22 septembre,
était encore déclarée hors du modèle au §3 et au §5. Et la durée requise des
emplois classés était détaillée deux fois dans « Ce qui reste hors du modèle » :
la puce de la catégorie active renvoie maintenant à celle qui la porte.

**Laissé tel quel.** « Vingt-deux exemples sont rejoués », dans « Ce qui vient
d'être refermé », était vrai le 17 septembre, et la section est `recit`.

**En chemin.** Les témoins périmés et le test du bloc d'exemple du README,
trouvés rouges sur `main` au début de la session, ont été réparés en parallèle
par une autre session, qui a aussi ancré, le même soir, les chiffres des
sections touchées ici : la fusion garde ses ancres, et la ligne de l'ENIM
porte les siennes.

**Fichiers.** `docs/limites.md`.

### 106. Le §4 de `limites.md` relu contre le modèle : une carte périmée, et une garantie deux fois trop chère — `fait`

**Demande.** Corriger les erreurs du §4 de `limites.md`, relevées en le
résumant le 22 septembre 2026. Les sous-sections `recit` n'ont été relues que
pour leurs contradictions internes, et n'en portaient pas ; les dix qui
disent l'état du dépôt l'ont été contre le code et les données.

**La carte des jeux de règles n'était plus ce qu'elle dit être.** Le texte la
donne pour la sortie de `calendrier_regimes.py --carte`, et vingt lignes
avaient bougé depuis — IRCEC, CAVEC, CNRACL, régime général, MSA. Elle est
régénérée depuis l'index LEGI, et la phrase qui disait les trois
complémentaires libérales à une seule période tombe : aucune ne l'est plus.

**Ce que les sessions du même jour avaient rendu faux.** La levée du plafond
des marins à cinquante-deux ans et demi, donnée pour manquante au tableau des
manques ; le RACD et le RACL « hors catalogue » ; la CARMF « sans série
historique », qui en a une de 1983 à 2026 ; la Cipav sans « fiche écrite » ;
la grille des forfaits des marins « introuvable ». Le cas type du navigant est
recalculé, décote de 2012 comprise — 52 121 € au lieu de 53 755 à deux fois
le salaire moyen ; celui du médecin est daté, `profession_liberale` portant
désormais la Cipav. La part patronale du public couvre huit régimes et non
neuf, la CNRACL jusqu'en 2028, et la RATP est découverte après 2025.

**Le scénario 6 portait encore la garantie d'avant le recensement**, comme
l'action 104 l'avait signalé : 1,30 % du PIB en 2026 pour 0,58, 40 milliards
pour 18, 1 621 cumulés pour 731, 12,9 milliards de plus pour l'impôt en 2024
pour 9,5. Le facteur de déplacement valait 0,61 et 1,14, non 0,64 et 1,26 ;
les reprises de 2070, 8,0 et non 7,7. Le coût de la garantie DÉPEND du poids
des femmes depuis que chaque sexe est déplacé du sien — lu à 56 % plutôt qu'à
52,8 %, il monte de 2,7 % —, et ce poids vient de `CaracteristiquesRetraites`,
non de `distribution.part_femmes`. Les hypothèses sans source sont sept et non
six. Les cumuls courent de 2025, première année projetée, et non de 2026.

**Et le rendement instantané.** Le §3 et la docstring de `scenarios/actuel.py`
le réservaient au RCI et au RAFP, « faute d'un prix d'achat publié ». Mesuré en
simulant les soixante-deux statuts à trois générations : le RAFP n'y passe
pas, il a sa série ; y passent les complémentaires des sections libérales et de
l'IRCEC, cinq petits régimes, et les années postérieures au dernier barème de
l'Agirc-Arrco, de l'Ircantec, du RCI et de la complémentaire des avocats. Le
plancher de base pour tous cumule 526 milliards, non 525 ; le scénario 6
n'ajoute pas « trois » limites mais une vingtaine. L'avance libérée de
150 000 € en 2070 est juste : 20 049 millions pour 2,77 millions de
bénéficiaires et 20,8 ans d'avance.

**Fichiers.** `docs/limites.md`, `src/retraite_notionnelle/scenarios/actuel.py`
(docstring).

### 107. L'électeur perdu : la réponse avant l'explication — `fait`

**Demande.** « J'aimerais que le site soit plus compréhensible. Actuellement,
ce n'est pas très aisé pour un électeur de s'y retrouver. Il faut que
l'électeur moyen ne se pose aucune question une fois qu'il a visité le site.
Il faut penser que l'électeur est perdu avec cette avalanche d'information. »

**Ce qui le perdait, lu au navigateur sur ordinateur et sur téléphone.** Tout
est vrai sur le site, et presque rien n'est dit dans l'ordre où l'électeur se
pose les questions. Après « Calculer », un téléphone montrait d'abord une clé
de lecture de cent soixante mots, puis dix nombres sur quatre barres — salaire,
retraite, « vraiment payé », trois montants sous la barre du système 4 — et
rien qui dise lesquels comparer ; puis un coefficient de conversion à cinq
décimales. La première question d'un électeur, « ma retraite va-t-elle
baisser ? », n'avait de réponse directe nulle part, et celle d'un retraité,
« et la mienne ? », était rangée à l'étape 2 d'un tableau replié. Dix onglets
de même poids, dont six de vérification (« Trajectoire », « Cas types »,
« Avantages », que l'électeur lit comme les avantages de la réforme). Et un
lien cassé : « Le système promet plus qu'il n'encaisse », dans la clé de
lecture, écrivait `#resultats-financement` à la place de la route, et
renvoyait à l'accueil en perdant la simulation.

**Premier geste, poussé seul : les résultats répondent avant d'expliquer.**

- *« En bref », en tête des résultats.* Trois phrases, avec les nombres des
  barres arrondis à l'euro et rien d'autre : ce que le système actuel promet
  et ce qu'il lui manque, ce que la proposition sert sans rien ajouter puis
  avec les cinq points rendus, et ce qui manque à elle aussi — dans les mêmes
  mots, « Elle non plus n'est pas entièrement financée », parce que taire le
  manque de l'une flatterait l'autre (action 62) ; enfin le salaire net, et ce
  qu'il en reste si l'on épargne les cinq points, sans quoi le lecteur
  additionnerait le plafond de la pension et le salaire plein. Un retraité
  parti avant la bascule y lit que sa pension « serait recalculée sur ce qui a
  été cotisé ». Le salaire est toujours le net : en brut, la proposition
  déplace surtout ce que l'employeur verse, et « votre salaire brut baisse de
  6 € » disait vrai d'une fiche de paie où le net monte de trois cents.
- *La clé de lecture nomme la proposition*, et dit des systèmes 2 et 3 qu'ils
  ne sont pas des propositions ; elle passe de cent soixante mots à
  quatre-vingts. Ce qu'elle disait après les chiffres qu'elle annonçait — le
  troisième n'est pas une prévision, la CSG au taux plein — est sous les
  barres.
- *Le coefficient de conversion et le capital notionnel* quittent la carte des
  repères pour « Le détail du calcul », à côté de la chaîne qu'ils servent à
  refaire. Restent les années cotisées et le « départ à la retraite », qui
  s'appelait « liquidation ».
- *« D'où vient cet écart de salaire »* replie les deux paragraphes sur la CSG
  et le taux d'équilibre public ; le chiffre, lui, reste ouvert.
- *Le lien cassé passe par `data-vers`*, et un test refuse désormais tout
  lien qui remplacerait la route par une ancre, sur toutes les pages.

La page de résultats compte moins de mots qu'avant, résumé compris : 1 026 au
lieu de 1 043. Aucun chiffre du modèle n'a bougé ; seuls les témoins des pages
ont changé, et le portage JavaScript les rend au caractère près.

**Deuxième geste : l'accueil répond aux questions de l'électeur.** Une
section « Vos questions », entre le tableau qui oppose les deux systèmes et
l'appel à vérifier : onze questions dans ses mots, chacune repliée sur trois ou
quatre phrases — ma retraite va-t-elle baisser, je suis déjà retraité, que
deviennent mes trimestres, à quel âge partir, ma fiche de paie, les petites
retraites, si je meurs, la Bourse, les fonctionnaires, le coût, la fiabilité
des chiffres. Les réponses ne disent que ce que le site établit ailleurs, et
renvoient à la preuve : vers une autre page par un lien, vers un dépliant de
l'accueil par `data-vers` — les neuf dépliants de « Pour aller plus loin » ont
reçu un identifiant pour cela. La phrase en gras de chacune est au catalogue
des affirmations, sous le contrôle qui tient déjà la même affirmation ailleurs
; une seule en demandait un nouveau.

- *La première réponse est celle qui coûte* : « Le plus souvent, elle sera
  plus basse que ce que le système actuel promet. » Le simulateur le montre en
  trois clics ; le taire ici aurait fait lire le reste comme une réclame. Le
  contrôle `proposition_le_plus_souvent_sous_la_promesse` le vérifie sur la
  grille des carrières types — plus de la moitié des cases négatives —, et
  tombera le jour où ce ne sera plus vrai.
- *Le retraité apprend ce que l'étape 2 du programme disait dans un tableau
  replié* : sa pension serait recalculée sur ce qui a été cotisé, revalorisée
  ensuite sur les prix, complétée par la garantie s'il le faut — une avance,
  reprise sur la succession.
- *La carte « 18 % + 5 % »* part du taux d'aujourd'hui, 28 % employeur compris,
  puis dit où vont ses points : 18 pour la retraite de tous, 5 placés à votre
  nom, 5 rendus sur le salaire. Elle alignait trois pourcentages avant le
  repère qui permet de les lire.
- *L'ASPA est nommée* « le minimum vieillesse » là où elle paraît sur l'accueil.

La liste se parcourt du regard et ne coûte rien au budget de lecture : 454 mots
de prose ouverte, pour 470.

**Troisième geste : le bandeau, en deux voix.** Programme, Simuler, Coût,
Pourquoi changer, Partager restent des onglets ; Cumul versé, Carrières types,
Droits non cotisés, Méthode et Sources passent derrière une étiquette qui se
voit, « Pour vérifier », en casse normale et plus petits. Sur un ordinateur de
1 280 points, le bandeau garde sa hauteur ; sur un téléphone, le groupe prend
sa rangée sous un filet. Les pages ont pris le nom de leur onglet, sur-titre et
titre du navigateur compris : « Risque » devient « Pourquoi changer »,
« Avantages » — que l'électeur lisait comme les avantages de la réforme —
« Droits non cotisés », « Trajectoire » « Cumul versé », « Cas types »
« Carrières types », « Données » « Sources ». Les adresses ne changent pas.

**Trois liens menaient à l'accueil sans le dire.** `#/methode/` et
`#/donnees/`, avec une barre de trop, depuis l'accueil et depuis les résultats
: le routeur ne connaît pas ces routes et rend le programme. Deux tests tiennent
désormais tout le site : un lien interne mène à une route qui existe, et un
`data-vers` vise une section présente sur la page qu'il désigne.

**Ce qui n'a pas bougé.** Aucun chiffre du modèle ; le nom du site, « Retraite
à comptes notionnels », que l'accueil explique dès sa première phrase et que le
site parent affiche dans son propre onglet ; les systèmes 2 et 3 sur la page de
résultats, que l'action 63 a nommés à la demande de l'utilisateur, et que la
clé de lecture présente maintenant pour ce qu'ils sont.

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `web/gabarit.py`,
`moteur/js/pages.js` et `moteur/js/gabarit.js`, `moteur/style.css`,
`data/reference/site/affirmations.yaml`, `tests/test_web.py`,
`tests/test_affirmations.py`, `tests/temoins/pages.json`, `README.md`,
`docs/integration-partiliberalfrancais.md`.

### 108. Le premier vrai relevé, et les six défauts qu'il a trouvés — `fait`

**Pourquoi.** L'action 85 avait ouvert le dépôt d'un relevé en PDF et l'avait
dit elle-même : la lecture n'avait jamais vu de vrai document, puisque aucun
n'est public. Elle a été confrontée à une estimation retraite d'Info Retraite le
22 septembre 2026. Le document sortait en lettres fausses, sans un seul chiffre.

**Ce que ce document est, exactement.** Il n'était pas intact, et son porteur
l'a dit : produit par `KslPrn`, le composeur d'Info Retraite, à 1 h 30, il a été
rouvert dans une suite bureautique (`ONLYOFFICE 9.4`) pour être anonymisé, puis
ré-exporté à 22 h 16 — les deux dates sont dans ses métadonnées, et ses polices
sont du Calibri, qu'aucune administration n'emploie. **Le contenu est celui de
la caisse ; le contenant est celui de l'éditeur**, et les six défauts se
partagent en conséquence. Les quatre défauts de LECTURE DU RELEVÉ viennent du
contenu, donc de la caisse : ses deux tableaux, ses unités écrites, ses lignes
qui ressemblent à une carrière sans en être une. Les deux défauts du LECTEUR DE
PDF ont été trouvés dans le contenant : les corriger est juste — la forme
tableau d'un `bfrange` est de la norme, le texte tourné existe partout, et les
deux documents de référence du dépôt y gagnent — mais rien ne dit qu'un PDF
intact d'Info Retraite les aurait exigés. **La confrontation à un document de
caisse INTACT reste donc à faire.**

**Ce que le document a trouvé, et qui est corrigé.** Six défauts, dont deux
dans le lecteur de PDF lui-même, qui servait déjà aux certifications du dépôt.

- *La forme TABLEAU d'un `bfrange`.* Une table `ToUnicode` écrit ses plages de
  deux façons — `<début> <fin> <destination>` et `<début> <fin> [ <dst> <dst> …
  ]` —, et ce document mêle les deux. La table venait de la suite bureautique,
  non de la caisse. L'expression régulière du lecteur
  cherchait trois hexadécimaux d'affilée : elle ignorait les crochets, lisait à
  cheval sur les entrées, et de proche en proche TOUTE la table se décalait.
  D'où « LQIRUPDWLRQ » pour « information » — et, les chiffres tombant sur des
  codes de contrôle, pas un seul nombre dans tout le document.
- *Le texte tourné.* Vingt-deux glyphes par page, posés à un quart de tour dans
  la marge, tombaient aux ordonnées des lignes du tableau et s'y inséraient :
  un revenu de 1 137 € devenait 203 568 €. La bande de lecture — droite ou
  tournée — entre désormais dans la clé de regroupement. Les deux documents de
  référence du dépôt y gagnent aussi : leurs titres courants verticaux et leurs
  étiquettes d'axe ne coupent plus les phrases.
- *Les deux tableaux d'un relevé.* Les trimestres sont dans l'un, les revenus
  dans l'autre, et aucun ne porte les deux. L'année se lit dans les deux à la
  fois.
- *Les unités écrites.* « 4 trim. », « 203,91 pts », « 49 150 € » : elles
  l'emportent désormais sur la position, qui reste le recours des tableaux
  muets. C'est ce qui permet de prendre à une ligne d'Agirc-Arrco sa durée sans
  prendre ses points pour un revenu — et de compter les 761 € d'une période que
  seule la complémentaire avait reportée.
- *Ce qui ressemble à une carrière sans en être une.* Un pied de page daté, une
  valeur du point à une date, une phrase française portant une année, un
  montant et des trimestres, des projections de départ jusqu'en 2066. Quatre
  règles les écartent : une période a deux bornes, une ligne de tableau n'est
  pas une phrase, elle porte quelques nombres et non quarante, et un relevé ne
  rapporte jamais l'avenir — le plafond se lit sur la date d'édition du
  document, et le site y ajoute l'année courante.
- *La couche de doublure.* Le PDF porte deux fois le même texte : une couche
  visible et une couche où toute une page est collée bout à bout. Additionnée à
  la première, elle faisait des revenus de deux millions d'euros. Elle vient de
  l'éditeur, et tout document rouvert pour être anonymisé en portera une : c'est
  le cas d'usage le plus probable de qui envoie son relevé à quelqu'un.

**Ce que ça a déplacé.** La carrière se lit maintenant en entier : onze années,
2014 à 2025, revenus et trimestres. Le contrôle est arithmétique et il vient du
document lui-même — il annonce **32 trimestres enregistrés**, et la somme de ce
qui est lu en fait 32. Les revenus se recoupent année par année avec le tableau
des périodes, employeur par employeur. Aucun chiffre du modèle ne bouge ;
`tests/test_releve_lu.py` porte le document en cas d'essai, sa mise en page et
ses pièges reproduits, les montants inventés.

**Ce qui reste.** Un PDF de caisse INTACT, d'abord : celui-ci était ré-exporté.
Et ce relevé-ci est celui d'un salarié du privé : les mises en page de la
fonction publique, des libéraux et des régimes spéciaux n'ont toujours pas été
vues. Et la couche de doublure ressort dans les lignes non
comprises, où elle n'apprend rien : le compte rendu montre les plus courtes
d'abord, celles qu'un lecteur peut reprendre à la main.

**Fichiers.** `scripts/fetch/lecture_pdf.py`, `moteur/js/lecture-pdf.js`,
`src/retraite_notionnelle/web/releve_lu.py`, `moteur/js/releve-lu.js`,
`index.html`, `tests/test_lecture_pdf.py`, `tests/js/lecture-pdf.test.js`,
`tests/test_releve_lu.py`, `docs/limites.md` §5.

### 109. Le §5 de `limites.md` relu contre le modèle, et un chiffre de la page Avantages qui dérivait — `fait`

**Demande.** Corriger les erreurs du §5 de `limites.md`, relevées en le
résumant le 22 septembre 2026.

**La recette du scénario 6 avait encore bougé.** −1,22 % du PIB de solde moyen
et non −2,16, coefficient 2040 à 0,83 et non 0,76, plus déficitaire que le
système actuel d'un dixième de point et 29 années sur 45, non d'un demi-point
et 38 ; la variante `rapport` à −0,53 % et 0,91. Le coût de la sortie des
impôts affectés est resté 1,395 point, et la table des mesures successives en
prend une quatrième ligne. Le RAFP est servi à son barème, non converti.

**Les six limites de fond.** Vingt-sept dispositifs sans chiffre sur
quarante-cinq, non vingt-quatre sur quarante-deux ; dix lignes lues dans les
sous-postes des comptes, non sept ; la surcote parentale est servie par la
grille, elle ne paie simplement rien avant 2026. Le tableau de la décote est
remesuré au diviseur par vingtile, qui est le défaut — 84,1 % et non 84,0,
puis 2,4, 7,0, 0,8, 4,2 et 6,4 points —, dans `limites.md` comme dans
`avantages_non_contributifs.md` ; la baisse de dépense va de 3,5 à 4,4 %, le
gain de solde de deux à cinq dixièmes. Le libéral a 3,1 ans de rente de plus
et 186 000 €, depuis que sa règle de départ a changé. Le contrôle d'isolement
de `avantages.py` n'est plus un refus pour la catégorie active.

**Un chiffre de page écrit en dur.** L'écart entre un agent actif et un
sédentaire partis à 57 ans était écrit dans `pages.py` — 825 € pour 1960, 102 €
pour 1965 — quand le modèle rend 680 et 84 ; `limites.md` disait la page
calculée. Elle l'est désormais, des deux côtés du portage
(`_ecart_plafond_decote`, `ecartPlafondDecote`).

**Fichiers.** `docs/limites.md`, `docs/avantages_non_contributifs.md`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`tests/temoins/pages.json`,
`tests/test_affirmations.py` (docstring).

### 110. Le simulateur garde ce qu'on lui a dit, et la page ne saute plus — `fait`

**Demande.** « Que le simulateur garde en mémoire ce qui lui a été mis comme
information. De plus, la page "saute" à chaque fois qu'on clique sur un
bouton. » (23 septembre 2026)

**Ce qui a été mesuré d'abord**, dans Chromium, à 1 280 et 360 points, avant
de toucher à quoi que ce soit.

- *Le saut.* Chaque clic sur une bascule, sur « Calculer », sur une année de
  la cascade faisait deux mouvements : en haut, puis plus bas. « brut » dans
  le formulaire : défilement 874 → 0 → 1 588 ; « Calculer » : 1 077 → 0 →
  1 588 ; une année de la cascade sur Coût : 3 992 → 0, et le dépliant de la
  cascade refermé. La cause était unique : `afficher` remplaçait la page par
  l'écran d'attente avant chaque calcul, la page tombait à quelques lignes, le
  navigateur ramenait le défilement à zéro, et `reprendre` redescendait ensuite
  aux résultats.
- *La mémoire, perdue de quatre façons.* Les bascules — en activité ou à la
  retraite, l'unité, le net ou le brut — sont des liens écrits au rendu depuis
  la saisie calculée : ce qui avait été tapé depuis disparaissait, et 3 333 €
  nets tapés devenaient, au clic sur « brut », les 4 423 € bruts des 3 500 € de
  l'exemple. Le formulaire d'un retraité ne renvoyait ni sa situation ni ce
  qu'il saisissait : « Calculer » le ramenait au formulaire d'un actif, sa
  pension ignorée, le calcul fait sur le salaire de l'exemple — le formulaire
  perdait de même l'âge de référence et l'âge de conversion réglés par
  l'adresse. Aller lire une autre page puis revenir par le bandeau rendait
  l'exemple de 1975. Et une saisie refusée se rendait sur le formulaire de
  l'exemple : une date de trop, trois métiers à retaper.

**Ce qui a été fait.**

- *Sur place, rien ne se vide.* Un rendu qui ne change pas de route garde la
  page, estompée, un trait d'or en haut de l'écran le temps du calcul. Les
  dépliants ouverts sont rouverts — reconnus à leur titre lu sans ses
  chiffres, celui de la cascade disant « De 422 Md € à 279 Md € » et changeant
  avec l'année. Ce qu'on a cliqué est retrouvé — le groupe de la bascule, le
  formulaire, l'ancêtre identifié — et reposé au même endroit de l'écran, le
  focus sur l'état choisi. « Calculer » descend aux résultats en un seul
  mouvement, doux sauf mouvement réduit ou arrivée d'une autre page. Dans le
  cadre de partiliberalfrancais.fr, c'est la page hôte qui défile, et la mesure
  se fait dans sa fenêtre.
- *La mémoire.* Le stockage local du navigateur garde, sous une seule clé, la
  dernière simulation que le lecteur a produite lui-même — par « Calculer »,
  par une bascule, ou en tapant — et ce qu'il a tapé depuis sans calculer. Qui
  revient sur Simuler sans carrière dans l'adresse la retrouve, l'adresse
  réécrite sans entrée d'historique ; une phrase prend la place de la
  consigne, et « Effacer ma saisie », à côté de « Calculer », vide la mémoire.
  Les règles suivent le lecteur : celles de l'adresse l'emportent, sauf tant
  qu'aucune page de la visite n'a été rendue sous d'autres règles que celles
  par défaut — une adresse sans règles n'est alors pas un avis. Le simulateur
  court de l'accueil montre la saisie retenue et l'envoie entière. Un
  navigateur qui refuse le stockage ne retient rien, et marche comme avant.
- *Les bascules refont leur adresse au clic*, sur ce que le formulaire porte,
  par `requeteBasculee` : la même traduction des montants que le rendu,
  `remplacementsUnite` et `remplacementsMontants` servant aux deux.
- *Le formulaire porte tout ce dont il dépend* : la situation et ce qu'on
  saisit, en champs cachés, et les deux réglages sans champ quand ils
  s'écartent du défaut. Une saisie refusée se remontre telle qu'elle a été
  envoyée : lue sans rien vérifier, les métiers jusqu'à la première ligne
  incomplète, que le script de la page remet dans la ligne vide qui l'attend ;
  ce qui ne se lit même pas ainsi repart de l'exemple sans perdre la forme du
  formulaire.
- *Trois phrases.* « L'exemple est déjà rempli » ne se dit plus qu'au-dessus
  de l'exemple. Le chapeau disait « rien n'est conservé » : il dit « votre
  saisie n'est gardée que par lui », le navigateur. Et le fichier d'un relevé
  n'est pas conservé, mais la carrière qu'il écrit l'est.
- *Les bornes du simulateur court.* Ses dates ne portaient pas leurs âges
  limites : les bornes du calendrier restaient celles d'un assuré né en 1975,
  et une naissance en 1990 rendait un départ à 64 ans impossible à envoyer.

**Ce que ça a déplacé.** Aucun chiffre du modèle : `simulations.json` est
intact. Après correction : « brut » 874 → 874, la bascule à 378 points du haut
de l'écran avant comme après ; « Calculer », un seul mouvement ; l'année de la
cascade 3 992 → 3 992, dépliant ouvert ; « Recalculer cette page » garde son
formulaire à un point près quand la page au-dessus grandit de 198 points. Le
parcours de mémoire — brouillon, rechargement, nouvel onglet, accueil, saisie
refusée, effacement, règles remises au défaut, stockage refusé — passe à
1 280 et à 360 points ; la bascule et le calcul, dans un cadre de même
origine.

**Ce qui reste.**

- La suite ne charge pas `index.html` dans un navigateur : ce qui précède a été
  vérifié par un script Playwright hors du dépôt. `tests/test_formulaire.py`
  tient ce qui se tient sans navigateur — le formulaire renvoie tout ce qu'il a
  reçu, la saisie refusée se remontre, le stockage n'est touché que par trois
  fonctions protégées — et `tests/js/bascules.test.js` la traduction des
  bascules. Un vrai essai de navigateur demanderait Playwright dans `.[dev]`.
- L'historique du navigateur garde les adresses des simulations, puisque
  l'adresse est la saisie : « Effacer ma saisie » vide la mémoire du
  simulateur, pas l'historique, et la phrase qui confirme l'effacement le dit
  ainsi.
- Saisie par la pension, les revenus de la carrière n'ont pas de champ et ne
  voyagent pas : repasser par « Ou saisir ce que vous gagniez » rend le revenu
  de l'exemple. Le simulateur court de la page Trajectoire n'est pas prérempli.
- Le bandeau se dit collé en haut (`position: sticky`) et ne l'est pas : son
  conteneur `#entete` a exactement sa hauteur, et il défile avec la page. Le
  coller demanderait une marge de défilement sur toutes les cibles — les
  résultats, le plan des pages longues, le lien d'évitement —, que ce chantier
  n'a pas touchées.

**Fichiers.** `index.html`, `moteur/js/pages.js`,
`src/retraite_notionnelle/web/pages.py`, `src/retraite_notionnelle/web/gabarit.py`
(`.envoi`, `.memoire`, le trait d'attente), `moteur/style.css` et
`tests/temoins/pages.json` régénérés, `tests/test_formulaire.py` et
`tests/js/bascules.test.js` (nouveaux), `tests/test_web.py` (une assertion).

### 111. L'audit du 23 septembre 2026 : formules, chiffres, tests et consignes — `en cours`

**Demande.** « Est-ce qu'on aurait pu faire des erreurs de formule
mathématique ? Des erreurs de chiffres ? Est-ce que des tests vérifient de
mauvaises choses ? Est-ce qu'il y a des consignes qui sont périmées ? », puis
« Corrige tout ». L'audit a rendu six lots ; ils sont menés dans l'ordre de ce
qu'ils déplacent.

**Lot 1, la mortalité — fait.** La mémoire des calibrations n'était indexée
que sur l'année et le sexe : les 112 lois de 2025 à 2080 étaient restées
calées sur les anciennes cibles saisies à la main, jusqu'à 1,1 an d'espérance
à 65 ans de trop. Chaque loi porte désormais l'empreinte de ses entrées, et
deux tests lisent la table que le modèle utilise, non une table recalculée.

**Lot 2, le scénario 1 — en partie.** Cinq règles écartées du texte, lues
dans l'index LEGI et chez la caisse, corrigées dans les deux moteurs, inscrites
au registre de veille et tenues par un test : le pourcentage maximum de la
pension civile, que les bonifications portent à 80 % (une mère fonctionnaire
de trois enfants, +6,5 %) ; la surcote qui s'ajoute au minimum contributif au
lieu de le multiplier (les deux exemples de la circulaire Cnav 2018-04) ; les
limites du chômage non indemnisé de R. 351-12, datées par la période (huit ans
validaient trente-deux trimestres, quatre au plus pour des années d'avant
2011) ; la fenêtre de la surcote parentale, qui est l'année précédant l'âge
légal (quatre trimestres aux générations 1965 à 1968, qui en recevaient zéro
à trois) ; les valeurs du point Ircantec de 2022 à 2026, versées par
`verifier_donnees.py` et non saisies dans le fichier. Deux tests mesuraient
autre chose que leur titre : la fenêtre parentale figée à trois trimestres
pour 1968, et la majoration de la fonction publique rapportée au total des
pensions, RAFP compris.

La majoration pour enfants, ensuite : à l'Agirc-Arrco, chaque point porte le
taux de son année d'acquisition (article 94 de l'accord du 17 novembre 2017,
table `majoration_enfants_points.csv`, l'exemple du dépliant de la caisse
rejoué) — une non-cadre de 1962 a sa pension Arrco majorée de 7,9 % et non de
10 ; les régimes spéciaux ajoutent 5 % par enfant au-delà du troisième, la
Banque de France sert 8,5 % puis 4,25 %, et les mines, l'Opéra et la
Comédie-Française, qui la servent, ne la déclaraient pas. Le témoin de la Cnav
rapportait la majoration de tous les régimes à toutes les pensions : il la
rapporte au régime de base.

Puis quatre valeurs datées à tort. Les durées de la suspension de 2026 ne
valent que pour les pensions prenant effet à compter du 1er septembre 2026 :
avant, les nés en 1964 et 1965 doivent 171 et 172 trimestres
(`duree_requise_avant_suspension.csv`), et les témoins de carrière longue de la
circulaire 2026-29, qui rejouaient sa règle en 2024 et 2025, liquident en
septembre 2026. Le minimum garanti de 2023 était celui de juillet 2022, le
plafond du minimum contributif de 2024 celui de novembre. Et les valeurs de
point qu'aucun barème ne couvre encore — le point RCO et celui de la CNAVPL en
2026 — se prolongent par les prix de l'année écoulée, comme la revalorisation
du 1er janvier, et non par ceux de l'année même. Le seuil de la première
tranche du RCI de 2014 à 2023 reste à lire : son effet est inférieur au
millième de la pension, et le registre de veille le déclare.

**Restent** les lots 3 (mécanique notionnelle et coût), 4 (chiffres du site
et données), 5 (tests mal orientés) et 6 (consignes périmées).

### 112. Le retraité voit la pension qu'il touche aujourd'hui, et un cas type la refait à la main — `fait`

**Demande.** « J'ai vu une erreur pour le cas retraités. Il montre le montant
de la pension à l'âge de départ à la retraite. Il faut montrer la pension
d'aujourd'hui. Il faut faire un cas type comme pour le cas d'une personne en
activité pour être sûr de notre coup. » (23 septembre 2026)

**Ce qui était faux.** Pour qui était déjà parti, la page le disait elle-même :
« ces montants sont ceux de votre pension au moment du départ […], et non de
celle que vous touchez aujourd'hui ». Elle affichait la pension du premier
mois, ramenée en euros de 2026 par l'indice des prix — comme si elle avait
suivi les prix. Elle ne les a pas suivis : gel de 2014, 0,3 % en 2019, cinq
coefficients en 2020 selon la retraite totale de décembre 2019, point Arrco
sans revalorisation plusieurs années de suite. Et la saisie par la pension
prenait le montant saisi pour celui du départ.

**Ce qui a été fait.**

- *Les revalorisations servies, lues à la source.* Le barème « Coefficients de
  revalorisation des retraites » de la Cnav, toutes les dates d'effet depuis
  1949 et les cinq tranches de 2020 (`scripts/fetch/cnav_revalorisation_pensions.py`) ;
  les décrets de revalorisation des pensions de l'État de 2004 à 2008, lus dans
  l'index JORF ; l'article 81 de la LFSS 2020 et l'article 68 de la LFSS 2019 ;
  L. 16 du code des pensions civiles et militaires dans ses trois rédactions.
- *Chaque régime revalorisé par son texte* (`revalorisation.py`, porté dans
  `revalorisation.js`) : les coefficients de la Cnav pour le régime général et
  les régimes alignés, la valeur de service de l'année pour les régimes en
  points — fusions et changement d'échelle de l'Arrco de 1999 compris —, le
  point d'indice puis les décrets puis L. 161-23-1 pour la fonction publique,
  la règle générale pour les régimes spéciaux, estimée avant 2009. L'ASPA
  d'aujourd'hui est recalculée à 65 ans révolus sur les pensions d'aujourd'hui.
  La majoration pour enfants suit, part par part, le régime qui la porte :
  les parts que l'action 111 a données à chaque régime ont remplacé, le jour
  même, le coefficient moyen de toutes les pensions.
  Les systèmes 2 à 4 suivent la règle que la page Coût prête aux comptes
  notionnels, et la garantie vieillesse du système 4 se recalcule sur la
  pension d'aujourd'hui.
- *La page.* Les montants d'un retraité sont ceux de 2026 ; la saisie par la
  pension vise la pension d'aujourd'hui — 1 600 € nets saisis sont 1 600 € nets
  en 2026 ; un dépliant « Votre pension, de votre départ à aujourd'hui » refait
  le chemin régime par régime, dit la tranche de 2020 et ce que la page
  affichait avant. L'affirmation « au moment du départ » quitte le catalogue ;
  « ces montants sont ceux de votre pension d'aujourd'hui » y entre, avec son
  contrôle sur le modèle.
- *Trois choses trouvées en chemin.* Une pension prise en janvier 2020 n'était
  pas servie en décembre 2019 : l'article 81 regarde la retraite « reçue […]
  le mois précédent », nulle, et le modèle lui prêtait son montant de départ.
  La phrase sur les systèmes 2 à 4 disait « jusqu'à la bascule, puis les prix »
  même quand le stock est réindexé. Et le réglage « pensions en cours à la
  bascule » se disait « page Coût seulement » : il joue désormais aussi sur la
  pension d'un retraité.

**Le cas type, refait à la main.** Un salarié non cadre né en janvier 1950,
au travail de 20 à 62 ans à 0,8 fois le salaire moyen, parti en janvier 2012.
Sa pension de départ, celle du modèle : 1 477,46 € bruts par mois. La base,
multipliée par les treize revalorisations du barème recopiées une à une,
×1,2215 ; la complémentaire, ses points servis à 1,4386 € au lieu de 1,2414 €,
×1,1589 ; 1 537,80 € en décembre 2019, donc 1 % en 2020. Sa pension de 2026 :
**1 780,61 € bruts, 1 618,57 € nets par mois**. La page lui en affichait
1 844,09 € bruts, 1 676 € nets — 3,4 % de trop. `tests/test_revalorisation.py`
refait ce compte sans le moteur ; le témoin `retraite_cas_type_2012` y tient le
portage JavaScript, et `tests/test_web.py` la page.

**Le cas type des autres.** Le COR publie, au rapport de juin 2026 (figure
3.14), le pouvoir d'achat de la pension nette d'un non-cadre et d'un cadre
partis en 1997, 2002, 2007 et 2012, année après année. Le dépôt le refait avec
ses propres séries : le non-cadre à moins de trois centièmes de point en 2026
pour les quatre générations, la génération 1952 à un quart de point chaque
année ; le cadre à 0,16 point en 2025, mais de 0,27 à 0,35 point en 2026,
l'année prévisionnelle du rapport, sans cause trouvée.

**Ce que ça a déplacé.** Aucun chiffre à la liquidation : les témoins ne
gagnent qu'un bloc `aujourd_hui` pour chaque carrière déjà liquidée, et le cas
type en entrée. Sur la page, la pension d'un retraité bouge d'autant que le
droit l'a revalorisée autrement que les prix. Mesuré ce jour-là sur une
carrière au salaire moyen partie à 62 ans, un départ tous les deux ans : de
2,2 à 5,8 % de moins pour les départs du privé de 1996 à 2020, cadres ou non,
et 1,5 à 1,8 % de plus pour celui de 2022, qui a reçu les 4 % anticipés de
juillet et les 5,3 % de 2024. Dans la fonction publique, jusqu'à 8 % de moins
pour les départs d'avant 2004, dont la péréquation n'est suivie que par le
point d'indice, et 4,7 à 5,7 % de plus pour ceux de janvier 2022 et 2024, qui
reçoivent la revalorisation du jour même de leur départ : les décrets de 2004
à 2007 la donnaient aux pensions « dont la date d'effet est au plus tard » ce
jour-là, et le modèle prolonge cette règle depuis 2009.

**Ce qui reste.**

- La confrontation à un DOCUMENT réel de retraité — une attestation de paiement,
  un avis de revalorisation —, comme l'action 108 l'a faite pour un actif.
- La péréquation de la fonction publique avant 2004 au-delà du point d'indice :
  les tableaux d'assimilation qui relevaient les pensions d'un grade réformé.
- Les régimes spéciaux avant 2009, dont les pensions suivaient les salaires de
  leurs actifs ; le régime de base des libéraux au-delà de sa dernière valeur
  de point publiée, et les régimes en points dont le dépôt ne porte pas la
  série des valeurs de service, comme la complémentaire de la Cipav — la règle
  générale en tient lieu. L'Ircantec, elle, a désormais ses valeurs jusqu'en 2026
  (action 111).
- La fonction publique depuis 2009 : aucun texte lu ne redit, sous
  L. 161-23-1, que la revalorisation du jour du départ est servie — le modèle
  le suppose, sur la foi des décrets d'avant. Et la tranche de 2020 d'une
  pension prise le 1er janvier 2020 : la lettre de l'article 81 est appliquée,
  aucune circulaire lue ne dit ce que le service des retraites de l'État a
  fait.
- L'écart du cadre du COR en 2026.
- Le graphique des cumuls reste bâti sur la pension du départ, et le dit.

**Fichiers.** `src/retraite_notionnelle/revalorisation.py` et
`moteur/js/revalorisation.js` (nouveaux), `simulateur.py`/`simulateur.js`,
`cout.py`/`cout.js` (la règle servie des systèmes notionnels y a déménagé),
`web/pages.py`/`pages.js`, `config.py` (docstring), `index.html` (le
préchargement du module), `scripts/fetch/cnav_revalorisation_pensions.py`,
`scripts/fetch/cor_pouvoir_achat_retraite.py`,
`data/reference/legislation/revalorisation_pensions.csv` et
`revalorisation_pensions_fonction_publique.csv`, `data/sources.yaml`,
`scripts/construire_donnees.py`, `scripts/construire_temoins.py`,
`scripts/mesures_prose.py` (mesure `aujourd_hui`), `tests/test_revalorisation.py`
(nouveau), `tests/test_web.py`, `tests/test_affirmations.py`,
`data/reference/site/affirmations.yaml`, `tests/temoins/`,
`data/reference/legislation/veille.yaml`, `docs/limites.md` §3.

### 113. De combien la retraite baisse : l'ordre de grandeur, dit à l'électeur — `fait`

**Demande.** « Tu ajouter l'indication de combien baissent les retraites entre
la situation actuelle et la situation du parti libéral français ? J'aimerais
qu'on donne l'ordre de grandeur pour que les gens aient une idée de la
baisse. » (23 septembre 2026)

**Ce qui manquait.** À « Ma retraite va-t-elle baisser ? », l'accueil
répondait « le plus souvent, elle sera plus basse que ce que le système actuel
promet », sans dire de combien. Le chiffre était ailleurs, carrière par
carrière — la glose de la barre 4, la grille des cas types —, et nulle part en
un ordre de grandeur. La page Carrières types, elle, ouvrait sur « Ces
pourcentages ne sont pas des baisses de pension » : une phrase du 17 septembre,
écrite quand on croyait le coefficient de la proposition supérieur à un, une
marge qui aurait relevé ses cases. Il est passé sous un le 20, et la phrase
était restée.

**Ce qui a été mesuré**, sur la grille — treize carrières, sept générations,
réglages de référence —, l'écart médian de la proposition au système actuel :

- 31 % de moins pour les cinquante carrières pas encore liquidées en 2026,
  sans rien ajouter : la répartition et les cinq points capitalisés
  obligatoires ;
- 24 % en plaçant les cinq points rendus, l'écart que la grille affiche ;
- 26 % sur la pension d'aujourd'hui des quarante et une carrières déjà
  liquidées, recalculée, garantie vieillesse comprise. Au départ, la grille en
  affiche 47 : la garantie ne s'ouvre qu'à 65 ans, et les deux pensions n'ont
  pas été revalorisées de la même façon depuis.

D'où « de l'ordre d'un quart à un tiers ». Quatre contre-épreuves, laissées
hors du site parce qu'elles disent la même chose : pondérées par les effectifs
de retraités de 2024, les trois médianes font 33, 25 et 27 % ; pour un couple
plutôt qu'une personne seule, 31, 24 et 27 % ; ramenées chacune au coefficient
d'équilibre de son année de départ, les carrières à venir perdent 29 % au lieu
de 24 — le réglage n'aurait pas relevé la proposition, il l'aurait abaissée ;
et en masse, la part contributive de la proposition — hors garantie, payée par
l'impôt, et hors rente capitalisée — est inférieure de 35 % à la dépense du
système actuel en 2026, de 30 % en 2040.

**Ce qui a été fait.**

- *Le modèle* : `castypes.ecarts_medians` et `EcartsMedians`, trois médianes
  basses de la grille, à la convention de `_deplacement_des_ecarts`.
- *Le bilan figé les porte.* `scripts/construire_donnees.py` les écrit dans
  `data/derive/equilibre.json`, sous `ecarts_medians`, et les deux portages
  les relisent (`EcartsFiges`). L'accueil ne simule toujours rien : il lit ces
  médianes comme la page des résultats lit les coefficients, sous les
  réglages de référence qui sont toujours les siens. Cinq secondes de plus à
  la construction.
- *L'accueil les dit à deux endroits.* Le tableau « Ce que cela change »,
  ouvert, gagne une ligne : « Votre retraite — ce que votre régime promet — de
  l'ordre d'un quart à un tiers de moins, en médiane ». La première question
  porte le même ordre de grandeur dans sa phrase en gras, puis les trois
  médianes et un lien vers la grille ; celle du retraité, la sienne.
  L'ordre de grandeur est CALCULÉ — la fraction la plus proche de chacun des
  deux écarts qu'on touche sans rien ajouter —, et non écrit : l'épargne
  volontaire n'entre pas dans le chiffre de tête.
- *Un paquet d'avant.* Le site lit son paquet en `force-cache` : un lecteur
  revenu avec le nouveau code et l'ancien paquet ne perd pas l'accueil, la
  réponse et le tableau se taisent sur le chiffre. Tenu des deux côtés.
- *La clé de Carrières types* dit « Ces pourcentages se lisent contre une
  promesse » : chaque case rapporte ce qu'un système servirait à ce que le
  système actuel promet à la même carrière ; ce que la grille mesure le plus
  sûrement reste l'écart entre ses lignes, et le niveau dépend aussi du
  coefficient. Démentir la baisse un clic après l'avoir annoncée aurait fait
  dire au site deux choses.
- *Le catalogue des affirmations* : trois entrées sous
  `ordre_de_grandeur_de_la_baisse`, qui recalcule les médianes case par case
  et exige que le bilan figé porte celles du modèle, et que ce soient des
  baisses ; la clé de Carrières types sous
  `les_cases_se_lisent_contre_la_promesse`.
- *Le parcours de présentation* faisait répondre « ce ne sont pas des
  baisses » à « tout est rouge, donc les pensions baissent ? ». Il répond
  désormais oui, par rapport à la promesse, et prévient que la diapositive 12
  du diaporama du 20 septembre dit l'inverse.

**Ce que ça a déplacé.** Aucun chiffre du modèle. Trois témoins de page —
l'accueil, Carrières types sous deux jeux de règles — et une clé de plus dans
le bilan figé. L'accueil passe de 215 à 233 mots de tableau ouverts, sur 240.

**Ce qui reste.**

- Carrières types n'écrit pas les médianes : sa prose ouverte est à quelques
  mots de son budget. La grille les montre case par case, et le simulateur la
  pension d'aujourd'hui d'un retraité.
- La diapositive 12 du diaporama du 20 septembre, fichier binaire daté.

**Fichiers.** `src/retraite_notionnelle/castypes.py`,
`src/retraite_notionnelle/donnees/bilan.py`, `moteur/js/bilan.js`,
`src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`scripts/construire_donnees.py`, `data/derive/equilibre.json`,
`moteur/donnees.json`, `data/reference/site/affirmations.yaml`,
`tests/test_affirmations.py`, `tests/test_web.py`, `tests/js/moteur.test.js`,
`tests/temoins/pages.json`, `docs/parcours_presentation.md`.

### 114. Aucune adresse nominative ne part sur GitHub — `fait`

**Demande.** Que rien, dans le dépôt, ne permette de remonter à une personne.
(23 septembre 2026)

**Ce qui a été cherché.** L'arbre courant ; chaque version de chaque fichier de
l'historique ; les messages et les signatures de tous les commits ; les
métadonnées des deux documents binaires (le PDF de l'OPEF, la présentation du
20 septembre) ; les releases, la pull request et les exécutions GitHub
Actions. L'arbre courant ne porte que l'identité du projet : le Parti libéral
français, son site, le compte `g-pliberal`. Ce qui désignait une personne était
ailleurs, dans les signatures de commits — auteur et committer —, qu'un poste
local tire de sa propre configuration git, et qu'un rebasage réécrit à
l'identité du poste qui le fait.

**Ce qui a été fait.** `scripts/pousser.sh` refuse désormais, sans rien
pousser, tout commit dont l'auteur ou le committer n'a pas une adresse
`noreply` (Anthropic, GitHub, ou `…@users.noreply.github.com`), et dit comment
le re-signer. Trois tests de `tests/test_pousser.py` le tiennent, dont celui du
committer que le rebasage du script pose lui-même sous un auteur anonyme.
`CLAUDE.md` donne l'identité à poser sur un poste local.

**Puis l'historique, le même jour.** Vingt-quatre commits, du 8 au 22
septembre, portaient de telles signatures ; un ancien nom du compte figurait
dans quarante-cinq versions de six fichiers et dans un message. L'historique
entier a été réécrit par `git filter-repo` : les signatures remplacées par
l'adresse `noreply` du compte, l'ancien nom par `g-pliberal` dans les fichiers
et par « l'ancien nom du compte » dans le message. Le contenu final de chaque
branche et de chaque tag est resté identique à l'octet, et aucun objet de
l'historique ne porte plus rien de nominatif. Toutes les empreintes ont changé :
les sept que citait ce journal ont été reportées, et `CLAUDE.md` dit comment
reprendre un clone antérieur, par `git merge-base --fork-point`. Ce qu'une
session ne peut pas faire reste à la main. Les deux tags, qu'elle n'a pas le
droit d'écrire, se replacent par `.github/workflows/tags-reecrits.yml`, à
lancer une fois depuis l'onglet Actions, puis à supprimer. GitHub sert les
anciens commits tant que son support ne les a pas purgés — la pull request
n° 1 les retient —, et les exécutions Actions qui les nomment se suppriment
depuis ce même onglet.

**Fichiers.** `scripts/pousser.sh`, `tests/test_pousser.py`, `CLAUDE.md`,
`README.md` et `docs/limites.md` (le compte des tests), ce journal (les
empreintes reportées), `.github/workflows/tags-reecrits.yml`.

### 115. Qui paie quoi : deux schémas de Sankey sur la page Coût — `fait`

**Demande.** « J'aimerais qu'on rajoute un diagramme de Sankey concernant les
coûts du système actuel sur un diagramme et les coûts sur le scénario du parti
libéral sur un autre diagramme. » (23 septembre 2026)

**Ce qui a été fait.**

- *Une troisième carte sur la page Coût*, « Qui paie quoi, aujourd'hui et avec
  notre proposition ? », posée après « Qui paie ? » et avant les notes. Deux
  schémas de Sankey, l'année de la bascule, sur le compte même du tableau
  « Recettes et dépenses, poste par poste » : à gauche ce qui paie — les quatre
  groupes de `GROUPES`, dans les couleurs du graphique « Qui paie ? », et ce
  qui manque, emprunté, en rouge comme le ruban d'écart du bilan —, au milieu
  la caisse, à droite ce qu'elle verse — pensions de droit direct, réversion,
  et ce qui reste, en vert, les années où il en reste. La proposition a trois
  caisses : le régime unique, que les cotisations alimentent ; le budget de
  l'État, qui paie la garantie vieillesse avec l'impôt ; le pilier capitalisé,
  placé au nom de chacun. Les deux schémas sont à la même échelle : un
  milliard y a la même épaisseur.
- *Une brique de plus au gabarit*, `sankey()` dans `gabarit.py` et son jumeau
  dans `gabarit.js`, identiques au caractère près. Un schéma est fait de
  caisses empilées, chacune alignée en haut avec ses payeurs et ses usages :
  aucun ruban ne croise un autre, aucun ne passe sous l'étiquette de la
  caisse, et l'écart entre deux nœuds d'une colonne est la hauteur de deux
  étiquettes, si bien qu'aucune n'est à écarter après coup. Le tableau des
  flux, de qui à qui et combien, est replié dessous. `echelle_sankey` tire
  l'échelle commune du plus gros des schémas.
- *Le compte de la bascule, lu une fois.* `_bilan_bascule` — `bilanBascule` en
  JavaScript — calcule l'année, le PIB, la garantie vieillesse lue sur la
  distribution des pensions et le pilier capitalisé ; le tableau poste par
  poste et la carte le lisent tous deux, et disent donc les mêmes nombres.
- *Le bouton « Partager » compose les schémas.* `imageDuGraphique` prend toutes
  les figures d'une carte, chacune aux proportions de son repère, le titre
  d'un schéma au-dessus de lui ; une courbe seule garde exactement la mise en
  page d'avant. Les étiquettes ont été taillées sur la police de REPLI : l'image
  dessine le SVG hors de la page, où Public Sans n'est pas chargée, et la
  police du système, plus large, rognait le « C » de « Capitalisation 5 % ».
- *La règle « deux graphiques, et pas un de plus » tient toujours* pour les
  graphiques dans le temps ; la carte des flux répond à une autre question,
  sur une seule année. Le budget de lecture de la page passe de 700 à
  950 mots — la carte en ajoute 230, dont 120 d'étiquettes. « Chaque euro a
  sa caisse » entre au catalogue des affirmations, avec un contrôle qui
  interroge le modèle : aucun impôt ni budget de l'État n'entre au régime
  unique, quand le système actuel encaisse les trois.

**Ce que ça a déplacé.** Aucun chiffre du modèle : les simulations sont
inchangées, et seuls les cinq témoins de la page Coût gagnent la carte. En
2026, au PIB de 2025, le système actuel brasse 423 Md € — 323 de cotisations,
contribution d'équilibre de l'État comprise, 64 d'impôts, 16 d'autres caisses,
15 du reste et 4,8 empruntés — pour 379 de pensions de droit direct et 43 de
réversion. La proposition en brasse 275 au régime unique — 227 de cotisations
à 18 %, 5,1 d'autres caisses, ce que l'assurance chômage verse et que le
régime garde depuis « Périodes indemnisées », le même jour, 7,0 du reste et 35
empruntés —, plus 15 d'impôt pour la garantie vieillesse et 63 placés au
pilier capitalisé. Sous les règles du témoin qui bascule en 2030, le régime
unique place 39 Md € au lieu d'en emprunter, et le schéma le montre en vert,
du côté des usages.

**Ce qui reste.**

- Sur un téléphone, le schéma défile comme la cascade : la moitié droite, ce
  qui est versé, se découvre en faisant glisser. Une disposition verticale
  propre aux écrans étroits le ferait tenir sans défiler.
- L'année est celle de la bascule, comme dans le tableau poste par poste. La
  cascade laisse choisir la sienne ; le schéma ne le fait pas encore. *Fait le
  jour même, voir plus bas.*
- L'image que compose « Partager » fait 1 200 × 2 100 : un fil la montrera
  recadrée, le premier schéma entier et le second en partie.

**Fichiers.** `src/retraite_notionnelle/web/gabarit.py` (la brique `sankey`
et son style) et `moteur/js/gabarit.js` ; `web/pages.py` et `moteur/js/pages.js`
(`_bilan_bascule`, `_caisse_flux`, `_cout_carte_flux`, le tableau poste par
poste qui lit le même compte) ; `index.html` (la composition de l'image) ;
`README.md` ; `data/reference/site/affirmations.yaml` ;
`tests/test_web.py`, `tests/test_affirmations.py`, `tests/temoins/pages.json` ;
`moteur/style.css`.

**Le 23 septembre 2026, plus tard : l'année des schémas se choisit.** Demande :
« Rends l'année des schémas réglable, comme la cascade. » Un sélecteur « Année
des schémas » est posé au-dessus des deux schémas, sur le modèle de celui de la
cascade : il offre les années de la cascade à compter de la bascule — avant
elle, le régime unique n'a pas de caisse à dessiner. L'année voyage dans
l'adresse, `#/cout?flux=2070`, comme une vue et non comme un réglage ; chacun
des deux sélecteurs garde dans ses liens l'année que l'autre a posée, et une
valeur qui n'est pas offerte retombe sur la bascule. Trois choses ont changé en
chemin.

- *Le compte d'une année.* `_compte_flux` — `compteFlux` en JavaScript —
  remplace, pour la carte, le compte de la bascule, que seul le tableau poste
  par poste lit encore. Chaque flux reste une part du PIB de son année,
  convertie en milliards par la règle que l'action 118 a donnée au site
  entier, `_pib_de_conversion` : une année projetée l'est au PIB de la
  dernière année publiée, et deux années se comparent ainsi flux à flux, sans
  que la croissance supposée grossisse le schéma.
- *La garantie vieillesse suit la trajectoire*, celle que la cascade pose, et
  non la lecture du tableau poste par poste, calculée une fois sur la
  distribution de l'enquête et qui n'a pas d'année. À la bascule, la carte dit
  donc 14 Md € où la ligne pour mémoire du tableau dit 12,9 — la plus basse
  des lectures que donne le dépliant de la garantie.
- *Les successions paient avec l'impôt.* Ce qu'elles rendent des avances de la
  garantie est une recette du budget de l'État la même année, et le schéma lui
  donne son ruban : 0,2 Md € à la bascule, 4,3 en 2070 sur une garantie de
  8,0, plus de la moitié.

Le budget de lecture de la page passe de 950 à 970 mots. Un témoin de plus,
`cout_flux_horizon`, pose les schémas en 2070 et la cascade en 2040 ; celui de
l'année refusée refuse aussi 2025 aux schémas. Fichiers : `web/pages.py` et
`moteur/js/pages.js` (`_annees_flux`, `_annee_flux`, `_vues_cout`, `_lien_vue`,
`_compte_flux`, `_cout_carte_flux`), `scripts/construire_temoins.py`,
`tests/test_web.py`, `tests/test_affirmations.py`, `tests/temoins/pages.json`.

### 116. Deux activités à la fois : le cumul se déclare, et le modèle ne devine rien — `fait`

**Demande.** Pouvoir cumuler plusieurs activités dans le simulateur, à
condition que la personne indique elle-même qu'il s'agit d'activités en plus :
rien ne doit être deviné. C'est aussi la réserve laissée par l'action 95, dont
le libéral n'a pas de carrière antérieure — mais celle-là porte sur un cas
type, et reste un chantier distinct.

**Ce qui existait.** Des activités SUCCESSIVES, jusqu'à six lignes dans le
formulaire, chacune déclarée — le statut d'une ligne n'est jamais
présélectionné. Rien pour deux activités sur la même période : les métiers
devaient se suivre, et le moteur ne tenait qu'une ligne, donc un statut, par
année civile.

**Ce qui est fait, dans les deux moteurs.** `Metier` porte `cumul` (faux par
défaut) et `age_fin`. Une activité cumulée s'ajoute à l'activité principale de
son âge de début à son âge de fin ou au départ, et l'année porte une ligne par
statut — deux lignes de la même année ne partagent jamais le leur, et
`ligne(annee)` rend l'activité principale. Chaque activité cotise à son régime
et chaque régime sert ses droits. Ce que le droit compte TOUS RÉGIMES — durée
d'assurance, durée cotisée, carrière longue, surcote, durée d'un groupe liquidé
ensemble — ne dépasse pas quatre trimestres par année civile : R. 351-5, le 2°
de R. 173-4-4-1 pour la réunion des régimes alignés, et l'article 20 du décret
n° 2003-1306 pour la CNRACL, tous trois lus dans l'index LEGI. La liquidation
unique somme les revenus d'une même année avant de les écrêter une fois au
plafond — la moitié de la Lura qu'un parcours à un métier à la fois ne
produisait jamais. Le compte notionnel porte la cotisation de chaque activité.

**Ce que ça a déplacé : rien.** Les témoins régénérés sont identiques au
chiffre près : aucune carrière à une activité ne bouge. La preuve de la règle
est dans `tests/test_cumul_activites.py` — un salarié au-dessus du plafond
qui ajoute une activité d'artisan garde la même retraite de base, parce que le
revenu de l'année est déjà écrêté et que la durée ne gagne rien sur des années
pleines ; le même salarié qui exerce en libéral reçoit la pension de la caisse
des libéraux en plus. Et quarante parcours cumulés tirés au hasard sont
confrontés valeur par valeur entre Python et JavaScript
(`tests/js/comparer-cumul.mjs`) ; une faute injectée dans le plafond annuel
du portage y a été prise.

**Le formulaire.** Chaque ligne de métier à partir de la deuxième porte un
menu « Cette activité : remplace la précédente / s'ajoute à celle en cours »,
réglé sur « remplace » — le comportement d'avant —, et une date de fin qui ne
sert qu'à l'activité ajoutée ; le script de la page la masque tant que
« s'ajoute » n'est pas choisi. Une date de fin sans cumul déclaré est refusée,
comme une période sans emploi déclarée cumulée, et le cumul en saisie par la
pension, qui ne cherche qu'un niveau pour toute la carrière. Le résumé du
parcours dit « et en même temps » là où il disait « puis », et « une année
n'a qu'une activité principale » là où il disait « qu'un statut ». Deux
simulations et deux pages témoins de plus, que le portage rend au chiffre et
à l'octet près.

**Deux trouvailles en chemin.** Le tirage au hasard Python/JavaScript a pris,
au rebasage, une interaction avec la limite du chômage non indemnisé arrivée
entre-temps sur `main` : le portage calculait la limite sur les lignes
principales puis rendait CE tableau-là, et les lignes cumulées, ajoutées
après, n'arrivaient jamais dans la carrière. Elles sont ajoutées au tableau
limité, comme en Python. Et un nom : la fonction qui crédite les trimestres
par année s'appelait `crediter`, comme celle que `main` venait d'écrire pour
les points majorés — le JavaScript refusait le doublon, le Python aurait
écrasé la première sans rien dire. Elle s'appelle `crediter_trimestres`.

**Ce qui reste.** Trois approximations que `limites.md` nomme : le plafond global d'assiette du compte notionnel
s'applique activité par activité, deux statuts qui versent au même
complémentaire y cotisent chacun sous un plafond entier, et la fiche de paie de
la page Rémunération ne montre que l'activité principale.

**Une leçon de manipulation.** Sous Windows, un fichier réécrit par un script
Python ouvert en mode texte repasse en CRLF, que `.gitattributes` refuse dans
le répertoire de travail. Ouvrir avec `newline=''`.

**Fichiers.** `src/retraite_notionnelle/carriere.py`,
`src/retraite_notionnelle/scenarios/actuel.py`,
`src/retraite_notionnelle/moteur/compte.py`,
`src/retraite_notionnelle/moteur/conversion.py`,
`src/retraite_notionnelle/simulateur.py`, `src/retraite_notionnelle/web/pages.py`,
et leurs portages dans `moteur/js/` (`regimes.js` pour la carrière longue),
`index.html` ; `scripts/construire_temoins.py`, `tests/temoins/` ; `tests/test_cumul_activites.py`,
`tests/js/comparer-cumul.mjs` ; `data/reference/legislation/veille.yaml` ;
`docs/methodologie.md`, `docs/limites.md`.

### 117. « Même moi je m'y perds » : l'accueil en une seule liste, et une légende qui montrait son code — `fait`

**Demande.** « Est-ce que le site est clair pour un nouvel arrivant ? Je
t'avoue que même moi je m'y perds par rapport à la quantité d'information qui
y est présente. Est-ce qu'il y a possibilité de condenser l'information et de
la rendre plus compréhensible pour tout le monde sans perdre le message ? »
(23 septembre 2026)

**Ce qui a été mesuré**, au navigateur, sur les dix pages, à 1 280 et à
390 points de large.

- *La page ouverte n'est pas ce qui perd le lecteur.* Les dix pages affichent
  environ 9 200 mots sans rien déplier, menus compris, et toutes tiennent leur
  budget de lecture. Ce qui les dépasse est derrière : environ 54 000 mots une
  fois tout déplié, dont 18 700 pour Coût seul, et une centaine de dépliants.
- *L'accueil disait chaque sujet deux fois, dans deux piles.* Onze questions
  de l'électeur, puis neuf dépliants « Pour aller plus loin » qui reprenaient
  les mêmes sujets dans la voix du programme — le plancher, la part
  capitalisée, les impôts, le coût —, et chaque réponse courte renvoyait plus
  bas vers l'un d'eux. Deux dépliants ne faisaient que redire : « Comment une
  pension serait calculée », les trois gestes affichés plus haut, et « Tout
  vérifier, page par page », un plan du site que le bandeau porte déjà.
- *Un défaut visible.* Sur Pourquoi changer, les légendes des deux premiers
  tableaux affichaient une ligne de `<span class="mot">` et de
  `role="button"` : un mot du glossaire posé dans une légende, que
  `g.tableau` échappe.
- *Ce qui reste à trancher*, et qui n'a pas été touché : voir « Ce qui
  reste ».

**Ce qui a été fait.**

- *Les deux légendes* redeviennent des phrases, des deux côtés du portage, et
  `test_aucune_page_ne_montre_de_balise_echappee` refuse toute balise échappée
  sur les dix pages. Poussé seul, en premier.
- *L'accueil n'a plus qu'une liste repliée* : treize questions, là où il y
  avait vingt titres en deux piles. Chaque développement est rangé derrière la
  réponse courte de la question qu'il traite, sous son titre d'origine — le
  plancher sous « Et les petites retraites ? », la part capitalisée sous « Mon
  argent sera-t-il placé en Bourse ? », les impôts supprimés sous la fiche de
  paie, les points de blocage sous le coût, la note signée sous « Ces chiffres
  sont-ils fiables ? ». Deux questions s'ajoutent pour ce qui n'en avait pas :
  « Pourquoi changer de système ? » (le système actuel, puis en quoi le compte
  serait plus juste, et un lien vers la page Pourquoi changer) et « Comment
  passe-t-on d'un système à l'autre ? » (les six étapes). Les deux dépliants
  qui redisaient sont partis ; « taux plein », « décote » et « surcote »
  gardent leur bulle, dans la réponse sur l'âge, qui renvoie aussi à Méthode.
- *Les renvois visent ce qu'ils nomment.* « Le calcul, en trois gestes » mène
  aux trois gestes eux-mêmes, et « Ce que cela change pour une veuve » au
  passage sur la veuve, non plus en haut du dépliant du plancher. Les
  identifiants des anciens dépliants sont portés par les questions qui les ont
  reçus.
- *La carte 02* perd la décomposition du taux d'aujourd'hui (11,3 % +
  16,7 %) et la phrase qui renvoyait au simulateur : quatre pourcentages au
  lieu de six, dans la carte la plus dense du premier écran. Ses quatre
  phrases du catalogue des affirmations sont intactes.
- *Une redite adjacente de moins* : « aucune action, aucun pari » se lisait
  deux fois dans le même dépliant une fois les deux rangés ensemble.
- `test_l_accueil_range_chaque_sujet_sous_une_seule_question` tient la liste
  unique, l'ordre des treize questions et la place de chaque développement.

**Ce que ça a déplacé.** Aucun chiffre du modèle : seuls les témoins de
l'accueil et de Pourquoi changer ont changé. L'accueil tout déplié passe de
5 199 à 4 884 mots, et de vingt dépliants à treize ; ouvert, de 454 à 439 mots
de prose. Les chiffres clés — 18 %, 5 %, 1 050 € — y reviennent autant de fois
qu'avant, mais chacun dans le dépliant de son sujet, la réponse courte puis
son développement, au lieu de deux endroits de la page.

**Ce qui reste**, proposé à l'utilisateur et non tranché ici, parce que chaque
point retire ou déplace quelque chose qu'une demande précédente a posé :

- *Le bandeau, sur un téléphone* : quatre rangées et dix liens avant le titre.
  Replier le groupe « Pour vérifier » derrière un seul bouton en ferait deux.
- *Dix pages, dont plusieurs se recoupent* : Cumul versé redit le dépliant
  « Ce que chaque système finit par verser » des résultats ; Méthode et
  Sources pourraient n'en faire qu'une.
- *Les montants au centime* sur les barres des résultats (« 3 840,19 ») là où
  « En bref » arrondit à l'euro.
- *Le même déficit en trois unités* selon la page : 5,1 Md € et 1,2 % de la
  facture sur Coût et Pourquoi changer, 0,17 % du PIB sur Carrières types.
- *« 10 % qui vous appartiennent »*, le titre de la part capitalisée, à côté
  de « 18 % + 5 % » sur la carte et de « 5 %, et ce que vous y ajoutez » dans
  la réponse qui le précède : dix, c'est cinq obligatoires et cinq que
  personne n'impose, et un nouveau venu lit deux chiffres pour une chose.

**Fichiers.** `src/retraite_notionnelle/web/pages.py`, `moteur/js/pages.js`,
`tests/test_web.py`, `tests/temoins/pages.json`, `README.md`,
`docs/parcours_presentation.md`.

### 118. Chaque part du PIB se lit aussi en euros, partout où le site en écrit une — `fait`

**Demande.** « J'aimerais que tout ce qui est identifié en % du PIB soit aussi
identifié en €. Certaines personnes sont plus habitués aux montants en euros.
Il y a déjà une partie du travail qui a été fait et il faut aller jusqu'au bout
de ce processus. » (23 septembre 2026)

**Ce qui existait.** Le tableau poste par poste (action 35, D), la note sur les
impôts rendus et le simulateur (action 62) disaient leurs parts en milliards,
au PIB de la dernière année publiée ; la cascade (actions 37 et 38) convertissait
les années projetées au PIB que le modèle projette, en euros courants de
l'année ; la trajectoire du modèle était en euros constants. Le reste, trente
endroits recensés sur cinq pages, ne parlait qu'en part du PIB : les quatre
graphiques qui en sont tracés, le tableau du solde et du coefficient, celui du
stock, la frise, la dette publique, les engagements acquis, le compte du COR
de la page Risque, les chiffres qu'elle cite du COR, de l'INSEE et de l'OCDE,
la carte « Le déficit » de Partager, le solde de l'accueil et de Cas types.

**Une seule règle pour tout le site** (`_pib_de_conversion`, `pibDeConversion`) :
une année dont l'INSEE publie le PIB se convertit au PIB de cette année-là,
c'est ce qui a été versé, encaissé ou dû ; une année projetée se convertit au
PIB de la dernière année publiée, et la page l'écrit, « au PIB de 2025 ». C'est
la règle de l'action 62 : un PIB de 2070 serait une hypothèse de croissance
déguisée en observation, et des euros de 2070 porteraient toute l'inflation
d'ici là. Seule la trajectoire du modèle garde ses euros constants, parce que
ses parts en sont tirées et que ses tableaux le disent.

**Ce qui a été fait.**

- *Les graphiques.* `g.graphique` prend un `pib` par année : chaque point de
  son tableau, donc de la lecture au survol qui le relit, s'écrit
  « 14,1 % · 422 Md € ». Le tracé ne change pas. Sous la carte de tête, une
  bulle dit la règle et ce que vaut un point, 29,9 Md € en 2025 : la carte
  était au plafond de son budget de lecture, et la bulle n'y compte pas.
- *Les tableaux.* La même forme dans la case, les deux unités côte à côte :
  solde et coefficient d'équilibre, stock de 2070 et sensibilité au taux,
  dépendance démographique (en euros constants), compte du COR de Risque.
- *La frise.* Chaque flux porte ses milliards sous sa part, chaque ligne du
  stock les siens alignés à droite. Les colonnes passent de 200 à 260 unités,
  pour que la réserve du système 2 tienne sans toucher sa voisine : 19,6 unités
  de blanc au plus serré, mesurées au navigateur sur les quatre frises.
- *La prose* des cinq pages, et les chiffres cités (les −0,2, −0,9 et −2,4 points
  du COR, les 3,7 et 6,3 points de l'INSEE, l'éducation et la recherche selon
  l'OCDE, Feldstein), leurs milliards au PIB de 2025.
- *Le README* : le tableau des soldes, les économies des scénarios 3 et 5, la
  dette, le retrait et les impôts affectés, par des sondes qui prennent
  `en=milliards` et suivent la même règle (`_milliards_de_part`).

**Trois choses corrigées en chemin.**

- *La cascade suivait une autre règle.* En 2070, elle disait la dépense du
  système actuel à 1 278 Md €, en euros de 2070 au PIB projeté, quand la carte
  du haut en donne désormais 458 au même endroit. Elle suit la règle du site ;
  le README, qui disait les impôts affectés de 2026 à 66 Md € au PIB projeté,
  en dit 64, comme la page.
- *Le tableau poste par poste* prenait le PIB de 2025 même pour une bascule
  réglée sur une année passée, et affirmait alors qu'un PIB publié ne l'était
  pas. La note restitution et le programme lisent le même PIB que lui.
- *La note sur la recette* du tableau poste par poste nommait encore
  l'assurance chômage parmi les versements retirés aux scénarios notionnels.
  La correction des périodes indemnisées, poussée le même jour, la leur
  laisse : la note ne nomme plus que la branche famille et le fonds de
  solidarité vieillesse, comme le dépliant des transferts.

**Ce que ça a déplacé.** Aucun chiffre du modèle : les simulations sont
identiques, les pages portent des milliards de plus, et le JavaScript rend le
même HTML que le Python. Les milliards n'ajoutent rien à la prose ouverte de
la page Coût : la règle y est dite dans une bulle, que le budget de lecture ne
compte pas. Les tableaux ouverts de Risque passent de 250 à 270 mots, dix cases
de quatre mots. Le HTML de la page Coût gagne 131 000 caractères, de 570 000 à
701 000, pour l'essentiel les tableaux des graphiques et la frise. Le test du
README confronte désormais ses milliards à ceux de la page.

**Ce qui reste.**

- Les documents. Les sections d'état de `methodologie.md` et de `limites.md`
  disent leurs parts en milliards, sauf deux : les dix points de dette que des
  primes de terme auraient déplacés, un contrefactuel écarté, et le contrôle
  externe du § 5 ter des limites, dont la page Coût donne la version en euros
  constants. Les récits datés n'ont pas à être réécrits, ce sont les chiffres
  d'un jour : les paragraphes du README et de ces deux documents que
  `zones.yaml` déclare récits, `risque_de_defaut.md`, cette feuille de route.
  `chiffrage_plf.md` dit déjà tout en milliards d'euros courants, comme un
  projet de loi de finances les demande.
- Sur téléphone, la légende du graphique de tête s'allonge : la case de la
  valeur réserve sa largeur, et « 14,3 % · 428 Md € » en prend plus que « 14,3 ».

**Fichiers.** `src/retraite_notionnelle/web/gabarit.py` et `moteur/js/gabarit.js`
(`milliards`, `part_et_milliards`, le `pib` des graphiques, la frise),
`web/pages.py` et `moteur/js/pages.js`, `scripts/mesures_prose.py`, `README.md`,
`docs/methodologie.md`, `docs/limites.md`, `tests/test_web.py`,
`tests/temoins/pages.json`.

### 119. Les complémentaires relues : le plafond du RAFP, et cinq trous que rien ne disait — `en cours`

**Demande.** « Il me semble qu'il manque encore pas mal de choses sur certains
régimes complémentaires. Tu peux me dire ce qu'il manque ? », puis, la liste
faite : « vas-y, commence par le plafond RAFP » (23 septembre 2026).

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

**Ce qui reste**, dans l'ordre où le prendre : les points gratuits de RCO
des chefs d'exploitation ; l'Arrco des ministres des cultes, statut à scinder ;
les ouvriers de l'État hors du RAFP ; le barème de l'Ircantec pour enfants ; le
routage calédonien et sa ligne d'inventaire ; les deux exceptions au plafond
du RAFP — la GIPA, cotisée en entier, les jours de compte épargne-temps
convertis — et la cotisation volontaire des agents de l'État outre-mer. La
ligne `rafp_assiette_plafond` du registre de veille et le récit de
`limites.md` (« Le RAFP prenait toutes les primes ») en tiennent le détail.

**Fichiers.** `data/reference/regimes/_schema.yaml` et
`data/reference/regimes/fonction_publique.yaml` ;
`src/retraite_notionnelle/donnees/regimes.py`, `scenarios/actuel.py`,
`moteur/compte.py`, et leurs pendants `moteur/js/regimes.js`,
`scenario-actuel.js`, `compte.js` ; `scripts/construire_donnees.py` ;
`tests/test_simulateur.py`, `tests/js/moteur.test.js`, les témoins ;
`data/reference/legislation/veille.yaml`, `data/sources_a_explorer.yaml`,
`data/reference/prose/zones.yaml`, `docs/limites.md`.

### 120. Le rapport de la Cour des comptes sur les retraites des fonctionnaires de l'État : une règle rendue au scénario 1, et ce qu'il reste à en tirer — `fait`

**Demande.** « Regarde ce rapport […]. Prends tout ce qui pourrait être utile
pour notre projet. » Le rapport est la communication de la Cour des comptes à
la commission des finances de l'Assemblée nationale du 22 septembre 2026, « Les
retraites des fonctionnaires de l'État » : cent dix-huit pages, lues en entier,
et les données de ses vingt-six graphiques, publiées à côté. `data/sources.yaml`
le porte sous `ccomptes_retraites_fpe_2026`, au statut `controle` : il n'alimente
aucune valeur, il en contrôle.

**Première règle : la durée d'un droit ouvert avant soixante ans.** Le tableau
n° 20 de l'annexe n° 3 donne la durée requise des emplois classés génération
par génération : 166 trimestres pour un super-actif né en 1965, 167 de 1966 à
1968, 168 jusqu'en août 1971 ; 168 pour un actif né en 1965 et jusqu'en août
1966. Le modèle opposait 169 au super-actif né en 1965, 169 ou 170 à ceux nés
de 1966 à 1969, 171 à ceux nés en 1970 et 1971, et 169 à l'actif né en 1965 et
1966. L'action 94 avait lu le
« a) » du XXIV de la loi de 2023 — « celle applicable avant l'entrée en vigueur
du présent XXIV » — comme l'ancienne table par génération ; il manquait la
seconde phrase du III de L. 13 dans sa version de 2014 (LEGIARTI000028498258),
relue dans l'index LEGI : « la durée des services et bonifications exigée des
fonctionnaires de l'Etat et des militaires qui remplissent les conditions de
liquidation d'une pension avant l'âge de soixante ans est celle exigée des
fonctionnaires atteignant cet âge l'année à compter de laquelle la liquidation
peut intervenir ». L'article 5, VI, de la loi de 2003 disait la même chose
depuis 2010, et l'article 66 de la même loi, par année d'ouverture, depuis 2004
— c'est la table de 2004-2008 que le dépôt lisait déjà à la bonne clé. Chaque
valeur de la Cour est la durée de la génération qui a soixante ans l'année où
le droit s'ouvre ; aucune n'est celle de la génération de l'agent. Et la
« non-monotonie que le texte assume », que l'action 94 croyait lire — 171
trimestres en juin 1971, 169 en octobre —, disparaît : 168, puis 169.

La règle vaut aussi pour le militaire, qui ouvre son droit à une durée de
services, avec deux étages de plus : avant 2004, la durée en vigueur était de
150 trimestres (« Jusqu'en 2003 : 150 », article 66) ; à compter du
1er septembre 2023, le C du XXIV lui en fixe une propre — 169, 170 en 2025, 171
en 2027, 172 dès 2028. Le modèle lui opposait la durée de SA génération, lue
à l'année de sa liquidation : 172 trimestres au sous-officier né en 1970 dont
le droit s'ouvrait en 2002.

`duree_requise_avant_soixante_ans.csv` porte les deux règles — par année
d'ouverture de 2009 à 2033, par date d'ouverture pour le C —, et
`_duree_requise_avant_soixante_ans` les lit quand la pension militaire ou le
classement de l'emploi ouvre le droit avant soixante ans ; les lignes de
`categorie_active.csv` qui portaient l'ancienne table sont vidées ou retirées.
Ce que cela déplace, génération par génération, pour un départ à l'âge
d'ouverture : de un à quatre trimestres de moins à l'actif né de 1954 à août
1966, de deux à six au super-actif né de 1959 à août 1971, de douze à quinze
au super-actif né de 1950 à 1953, dont le droit s'ouvrait avant 2004. En
pension, à soixante ans pour l'actif et à cinquante-sept pour le super-actif :
+1,22 % à l'actif né en 1957, +0,60 % à ceux nés en 1962 et 1965, +3,09 % au
super-actif né en 1960, +1,81 % et +1,79 % à ceux nés en 1965 et 1970. Pour un
militaire entré à dix-huit ans et parti à quarante-cinq : +14,67 % au né en
1970, +3,58 % au né en 1980 ; rien aux nés de 1985 et 1990, dont les services
atteignent déjà le pourcentage maximum. Neuf lignes du tableau n° 20 entrent
dans `exemples_officiels.yaml`, où la Cour devient le quatrième éditeur admis :
elle n'applique pas la règle, mais elle est la seule à publier cette table.

**Une seconde règle, que l'action 119 a portée le même jour.** Le rapport
rappelle aussi que la RAFP ne retient les primes que dans la limite de 20 % du
traitement indiciaire — l'article 2 du décret n° 2004-569 dans toutes ses
versions depuis 2004 —, ce que la fiche écrivait sans qu'aucun moteur le lise.
Cette session l'avait codé de son côté ; l'action 119 l'a poussé la première,
avec un champ de période (`plafond_primes_traitement`) et un découpage unique
du revenu (`part_du_revenu`), et c'est sa version qui reste. Le rapport en est
une confirmation de plus.

**Ce que les témoins ont vu.** Seuls des cas de la fonction publique bougent ;
les autres écarts du fichier des simulations sont au seizième chiffre. Les
emplois classés, sur l'État, la CNRACL et les ouvriers de l'État :
+2,06 % de pension au cas né en 1945, dont le droit s'ouvrait à cinquante-cinq
ans en 2000 et qui se voit opposer 150 trimestres au lieu de 160 ; +1,16 % à
celui né en 1955 (162 au lieu de 166) ; +1,20 % à celui né en 1965 (168 au lieu
de 169 pour l'actif, 166 pour le super-actif). Les militaires : leur pension
du scénario 1 ne bouge pas, leurs services atteignant le pourcentage maximum,
mais la durée qu'on leur oppose — 150 trimestres au lieu de 170 pour le
sous-officier né en 1965, 162 pour l'officier — relève les droits acquis que le
scénario prospectif convertit : +6,2 % de pension figée pour le premier. Les
agrégats bougent à peine : la dépense du système actuel en 2070 passe de 18,26
à 18,25 % du PIB, de 711 à 710 milliards, parce que la dépense de 2024 est
calée sur l'observé et que la correction relève les pensions des générations
parties avant 2023 sans toucher celles de 2070 ; les avantages chiffrés de
2024, de 96,3 à 96,1 milliards, dont la ligne de la catégorie active de 0,6 à
0,7.

**Trois tests et une phrase du site disaient l'ancienne lecture.** Les tests de
l'action 94 attendaient 169 trimestres pour l'actif né en 1965, 168 pour celui
né en 1963, et « l'escalier qui redescend » — 171 puis 169 — pour le super-actif
de 1971 ; ils attendent désormais 168, 167, et 168 puis 169. La page Avantages
écrivait que le classement abaisse la durée requise « d'un trimestre » pour la
génération 1965 : il l'abaisse de quatre, et d'un pour 1960, et la phrase le
calcule désormais des deux côtés du portage (`_ecart_duree_classement`).

**Ce que le rapport confirme, et deux écarts qu'il explique.** Le minimum
garanti de 2026 (1 366,35 € par mois), la valeur du point (4,923 € depuis
juillet 2023), la retenue de 7,85 % en 2010, 9,54 % en 2015 et 11,10 % depuis
2020, les taux de contribution de l'État de 2006 à 2026 (graphique n° 23), le
minimum contributif majoré de 2026. Deux écarts, sans correction. La Cour
donne 58,47 % pour l'État en 2009 là où le dépôt porte 60,14 % : c'est la
moyenne de l'année, le taux ayant été ramené à 40,14 % en décembre (note 3 du
jaune pensions 2026, qui fait de même pour 2013, à 44,28 % — ce que la Cour ne
reprend pas, son graphique donnant 74,28 % pour 2013). Et le plafond
d'écrêtement du minimum contributif qu'elle cite, 1 410,89 € par mois, est
celui du 1er janvier 2026, quand le dépôt porte celui du 1er juin (1 444,89 €,
circulaire Cnav 2026/16) — le barème de la Cnav, lisible par son interface
(`/api/v1/baremes/baremesByFileLeafRef/retraite_personnelle_minimum_plafond_retraite_bar.aspx`),
les donne l'un et l'autre avec leur circulaire. Ce barème montre en revanche
un écart que le rapport n'a pas visé : 1 394,44 € au 1er novembre 2024 et au
1er janvier 2025, là où le dépôt porte pour 2025 1 394,86 €, le plafond de
janvier 2024 relevé de 2 % ; quarante-deux centimes par mois, que le
récupérateur de ce barème, à écrire, trancherait.

**Ce que le rapport apporte et qui reste à prendre.** Classé par ce que
chaque chantier déplacerait.

1. *La décomposition du taux de contribution de l'État.* Le compte
   d'affectation spéciale appelle 78,28 % du traitement en 2025 pour un civil
   et 126,07 % pour un militaire ; la Cour les décompose, en méthode qu'elle dit
   réplicable chaque année, et n'en garde que 44,1 % et 51,2 % pour la retraite
   au sens strict : 0,4 et 1,9 point pour l'invalidité avant 62 ans, 2,4 et 3,4
   pour les majorations pour enfants, 1,5 et 33,8 pour les départs anticipés
   (« avantages professionnels »), 35,3 et 21,9 pour le déséquilibre
   démographique (tableau n° 15). Le scénario 4, et le 6 jusqu'à la bascule,
   créditent aujourd'hui au compte la retenue et le taux civil du CAS,
   militaires compris. Deux
   questions en sortent, qui ne se tranchent pas sans l'utilisateur : le
   militaire, dont l'employeur paie 126,07 %, doit-il se voir créditer le taux
   civil ; et la part du taux qui finance l'invalidité, la solidarité et la
   démographie est-elle une cotisation de l'assuré ? La décomposition de la
   Cour est la réponse chiffrée que « La part patronale du public, et ce qu'on
   n'en sait pas » (`limites.md`) attendait ; l'Institut des politiques
   publiques, par une autre méthode, trouvait 34,7 % en 2020 (annexe n° 6).
2. *La part des primes des cas types*, 18 %, 22 % et 25 %, n'a pas de source.
   La Cour donne 20,0 % en 2015 et 23,1 % en 2023 pour l'ensemble des
   fonctionnaires de l'État (graphique n° 13), 14 % dans l'enseignement
   supérieur, 33 % aux ministères économiques et financiers, 60 % aux affaires
   étrangères en 2024, et un cas type de catégorie B dont la part passe de 26 %
   à 35 % de 2025 à 2050. Le paramètre commande le traitement indiciaire, donc
   la pension civile ; au-dessus d'un sixième, la retraite additionnelle ne
   suit plus les primes mais le traitement, que son plafond vise.
3. *L'espérance de vie à 65 ans par catégorie*, moyenne 2015-2024 (tableau
   n° 9) : 21,22 ans pour un homme sédentaire, 19,65 pour un super-actif,
   19,91 pour un ancien de La Poste, 19,78 pour les autres actifs ; 24,57 et
   24,84 pour une sédentaire et une institutrice. L'action 14 donne aux
   fonctionnaires un facteur de mortalité unique ; l'espérance de vie des
   emplois classés y est plus courte d'une année et demie, ce que le diviseur
   ignore.
4. *Les bonifications des militaires*, hors du modèle : le cinquième pèse
   environ 10 % de la pension des militaires partis en 2025, les bénéfices de
   campagne 7 %, les services aériens et sous-marins 5 %, et un quart de leur
   durée validée (37 trimestres sur 150, génération 1953). C'est elles qui
   décideraient si la durée requise, désormais juste, mord sur un militaire.
5. *La même règle de durée dans les régimes spéciaux.* Le lot de l'action 89
   a donné le même jour à la SNCF, à la RATP et aux IEG leur table par
   génération (`duree_requise_regimes_speciaux.csv`), et lu « la durée d'avant »
   comme l'ancienne table par génération — la lecture que l'action 94 avait
   faite pour la fonction publique. Or l'index LEGI porte, au mot près, « avant
   l'âge de soixante ans […] l'année à compter de laquelle la liquidation peut
   intervenir » dans les versions de 2017 à 2023 de l'annexe 3 du statut des
   IEG, dans l'article 23-1 du règlement de la RATP et, à cinquante-cinq ans,
   dans l'article 12-1 du décret de la SNCF — l'un et l'autre « jusqu'au
   31 décembre 2024 » —, et dans les régimes de la Banque de France, de l'Opéra
   et de la Comédie-Française. Ces tables sont à relire à la même lumière.
6. *La comparaison à la littérature.* La DREES (Chopard et al., 2022, modèle
   Trajectoire) trouve qu'un sédentaire né en 1958 aurait une pension
   supérieure de 1,5 % sous les règles du privé, avec 62 % de gagnants et
   32 % de perdants, et aurait versé un quart de cotisations salariales de
   plus ; la Cour montre sur un cas type que les vingt-cinq meilleures années
   valent 15 % de plus que le dernier traitement si le point est gelé, 5 % s'il
   suit le tiers des prix, 8 % de moins s'il suit les prix et 30 % de moins s'il
   suit les salaires (tableau n° 6). Deux points de comparaison pour le
   § 5 quater de `limites.md`.
7. *Les effectifs.* Les cotisants et les retraités des civils et des
   militaires de 2015 à 2025, et leur rapport projeté jusqu'en 2050
   (graphiques n° 1, 4 et 10), là où `cotisants.csv` les porte sur une seule
   ligne ; les anciens de La Poste et d'Orange, 50 000 cotisants pour 290 000
   pensionnés en 2026.
8. *À surveiller.* Le Président de la République a annoncé le 14 juillet 2026
   l'intégration d'une part des primes des militaires dans le calcul de leur
   pension à compter de 2027 : rien au Journal officiel à cette date. Le
   rapport note aussi que la loi de financement pour 2026 transforme en
   bonification l'un des deux trimestres de majoration par enfant né depuis
   2004 — ce que `majoration_duree_assurance.csv` porte déjà.

**Fichiers.** `data/reference/legislation/duree_requise_avant_soixante_ans.csv`
(nouveau), `data/reference/legislation/categorie_active.csv`,
`src/retraite_notionnelle/scenarios/actuel.py`, `moteur/js/regimes.js`,
`moteur/js/scenario-actuel.js`, `scripts/construire_donnees.py`,
`data/reference/legislation/veille.yaml`, `data/sources.yaml`,
`tests/temoins/exemples_officiels.yaml`, `tests/test_oracle.py`,
`tests/test_simulateur.py`, `src/retraite_notionnelle/web/pages.py`,
`moteur/js/pages.js`, `docs/limites.md`, `docs/methodologie.md`,
`docs/parcours_presentation.md`, et les fichiers fabriqués.
