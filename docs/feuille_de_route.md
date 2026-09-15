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
témoins. Les actions 1 à 3 ne touchent que les données et la page Coût ; les
actions 5 et 7 touchent les deux moteurs.

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

### 3. Certifier les taux de cotisation, matière des scénarios 2 à 6 — `à faire`

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

### 4. Étendre la contre-expertise du scénario 1 — `à faire`

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

---

## Second rang — réel, mais plus cher ou plus étroit

### 5. Catégorie active et militaires — `à faire`

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

### 6. Le solde, et non le coût — `à faire`

**Pourquoi.** La page Coût dit ce qui est versé, jamais ce qui est encaissé
(`cout.py`, réserve 4). Un système notionnel réel se définit par son
équilibre ; sans recettes, ni coefficient d'équilibre ni rendement implicite ne
sont calculables, et `limites.md` §5 le signale comme hors champ.

**Sources.** DREES, Comptes de la protection sociale, ressources par risque
(même source que `depenses_retraite.csv`) ; CCSS pour le régime général.

**Marche.** Une série de recettes à côté de `data/reference/macro/depenses_retraite.csv`,
le solde observé, puis le coefficient d'équilibre qu'exigerait chaque scénario
année par année. Ne touche pas les moteurs de pension.

### 7. Saisir un relevé de carrière réel sur le site — `à faire`

**Pourquoi.** Le chemin le plus exact, `Carriere.depuis_lignes`, n'est
accessible qu'en Python. Le site plafonne à six métiers et des interruptions
par plage. Un relevé collé année par année permettrait à chacun de confronter
le simulateur à son estimation Info-Retraite : c'est le levier de crédibilité
le plus fort du projet.

**Marche.** Un format texte simple (année, régime, revenu, trimestres),
analysé dans `moteur/js/pages.js` et dans `web/pages.py` à l'identique, porté
dans l'adresse comme le reste des paramètres, avec des témoins. L'import
automatique reste impossible (`limites.md` §5, « Les carrières réelles »).

### 8. Faire liquider chaque cas type à l'âge de SA génération — `à faire`

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
