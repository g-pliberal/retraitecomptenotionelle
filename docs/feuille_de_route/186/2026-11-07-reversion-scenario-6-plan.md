# La réversion au scénario 6 : le plan, et le stock gardé au coût

**Reprise, au 7 novembre 2026.** Étape 1 faite : le coût du scénario 6 garde
les réversions servies à la bascule jusqu'à extinction (décision 16). Le
site le dément encore à cinq endroits, déclarés `contredite` (action 186) au
catalogue des affirmations, dont la cascade de la page Coût, qui tombe court
de la réversion gardée. Par quoi commencer : l'étape 2, le site qui dit le
stock gardé, cascade d'abord ; puis la garantie d'office (étape 3), le stock
au simulateur (4), la rente sur deux têtes (5), le décès d'un actif (6), le
README (7). Une étape par session, chacune sa note ici, et ce bloc récrit
par chacune ; le détail est sous « Le plan ».

**La demande.** Le 7 novembre 2026, le propriétaire ouvre une session du
modèle pour porter au scénario 6, et à lui seul, les décisions 16 à 28 du
programme sur la réversion (`docs/feuille_de_route_programme.md`,
chantier 3) : un plan en étapes, et la première menée jusqu'à `main`.

**Ce que le propriétaire a précisé, le même jour.** Deux questions que
l'étude ne tranchait pas :
- *Le scénario 6 est rétroactif : que montre-t-il de la réversion avant la
  bascule ?* « Servie avant » : la règle se lit « décès avant la bascule :
  réversion du droit actuel ». Avant 2026, tous ceux qui touchent une
  réversion ont perdu leur conjoint avant la bascule ; le scénario 6 la sert
  donc entière, comme les scénarios prospectifs, et la courbe est continue.
- *Sur quoi le stock gardé se revalorise-t-il ?* « Sur les prix », comme
  aujourd'hui et comme l'étude l'a chiffré (H1).

La garantie servie d'office (décision 20) ne se pose pas hors du scénario 6 :
la garantie n'existe que là (`COMPOSANTE_GARANTIE`), et la décision 28 borne
les décisions 16 à 27 au scénario 6. L'ASPA des scénarios 1 à 5, que l'effet
retour chiffre au même taux de recours (`effet_retour.py`), garde donc le
non-recours de la DREES : l'étape 3 sépare les deux taux.

## Ce qui est fait : le stock gardé au coût (étape 1)

- `src/retraite_notionnelle/reversion_gardee.py` : `StockDeReversion`, la
  part de la masse du stock, en euros constants, servie chaque année. Le
  stock a l'âge et le sexe des veufs de 60 ans ou plus de l'INSEE
  (`etat_matrimonial.csv`, 1er janvier 2020, la dernière année publiée), les
  90 ans ou plus étalés comme les survivants d'une génération ; il meurt
  comme la population générale (`DonneesMortalite`), sous l'hypothèse
  d'espérance de vie du calcul ; les femmes touchent 91,5 % de la masse
  (COR, novembre 2025), là où l'étude posait sans source qu'un veuf touche
  40 % de ce que touche une veuve. Âge moyen à la bascule : 80,5 ans.
- `cout.py` : `masse_du_scenario` prend `part_gardee`, que seul le scénario 6
  sert (`CLES_REVERSION_GARDEE`) ; `CoutAnnuel`, `AvenirAnnuel` et
  `SoldeAnnuel` portent `part_reversion_gardee`, un avant la bascule, puis le
  stock rapporté à la réversion du droit actuel de l'année
  (`_garder_les_reversions`), le stock valant la réversion de l'année qui
  précède la bascule. Les appelants de `masse_du_scenario` la passent tous
  (`facteurs_depense.py`, `donnees/agregats.py`,
  `scripts/cout_age_depart.py`).
- Ce qu'il sert, en Md€ courants, face à la table de l'étude : 43,1 en 2026
  (43,1), 36,3 en 2030 (36,5), 20,0 en 2040 (20,3), 8,2 en 2050 (7,8), 1,6
  en 2060 (1,5), rien en 2070. La moitié du stock est éteinte en 2035.
- Le solde moyen 2026-2070 du scénario 6 passe de −1,08 à −1,44 point de
  PIB : 0,36 point, le coût brut du stock gardé (1,19 − 0,82 dans l'étude).
  Le système actuel est à −1,14 : le scénario 6 fait désormais moins bien
  que lui en moyenne, avant que la garantie ne voie la réversion gardée
  (ci-dessous). Ses chiffres ancrés bougent (solde moyen, dette, année du
  coefficient minimal, qui passe de 2048 à 2026) : GitHub les récrit, mais
  la prose qui les entoure est à relire (étape 2 et 7).
- Les tests : `tests/test_reversion_gardee.py` (la règle de masse ; le stock
  qui s'éteint de moitié en neuf ans, à l'âge moyen de 80 ans) ;
  `tests/test_cout.py` (le stock servi, chiffré sur la table de l'étude à un
  dixième près ; les scénarios 2 à 5 sans réversion ; le gain de la
  convention `supprimee`, 0,82 point au scénario 6 contre 1,19 aux autres) ;
  six tests du coût récrits, qui tenaient le scénario 6 sans réversion.
- Le catalogue des affirmations : les phrases « Notre système ne sert aucune
  réversion » (accueil, deux entrées) et « Seul le système actuel sert la
  pension de réversion » (Coût) passent `contredite`, action 186, sous le
  contrôle `scenario_6_garde_les_reversions_servies` ; les deux phrases de la
  cascade aussi, leurs contrôles tenant qu'elle tombe court exactement de la
  réversion gardée. Le contrôle de la garantie hors de la masse retire la
  réversion du scénario 6 avant de le comparer au scénario 4.
- `docs/limites/5-bis-cout-agrege.md` dit la règle des scénarios 2 à 5 et
  celle du scénario 6.

**Limites.** La garantie vieillesse du scénario 6 se calcule sur les seuls
droits directs : elle ne voit pas la réversion gardée, qu'elle devrait
déduire, ni celle qui manque aux décès à venir (l'étude chiffrait cet effet
net à côté du modèle). Les veufs de moins de 60 ans, que la fonction publique
sert sans condition d'âge, sont hors du profil. Dans chaque sexe, chacun
touche autant. Le profil est celui de 2020, pris pour celui de la bascule.

## Le plan, une étape par session

Chaque règle du moteur d'une carrière s'écrit d'abord en JavaScript, son
jumeau Python suivant (`src/CLAUDE.md`) : le portage n'est donc pas une étape
à part, il est dans les étapes 4 à 6.

2. **Le site dit le stock gardé** (zone du site, liste de `moteur/CLAUDE.md`).
   La cascade de la page Coût d'abord : `marchesCascade` et son arrivée
   (`pages.js`, autour de la ligne 11420 et 11630) portent la réversion
   gardée, qu'il faut sérialiser au paquet (`part_reversion_gardee`, dans
   `donnees/agregats.py` et `moteur/js/agregats.js`) ; la marche « Réversion
   supprimée » et son libellé (`MARCHES_HORS_SYSTEMES`) ; puis les phrases
   contredites, l'accueil (« Notre système ne sert aucune réversion », vers
   la ligne 16833) et la page Coût, leurs entrées rendues à `verifiee` ; la
   prose autour des chiffres ancrés qui ont bougé
   (`docs/parcours_presentation.md`, l. 269 et 396 ;
   `docs/limites/5-ter-trajectoire.md`, l. 382-384 ;
   `docs/limites/4-regimes-incomplets.md`, l. 791-798 ; le README,
   l. 926).
3. **La garantie servie d'office** (décision 20) : un recours de 100 % pour
   la garantie du scénario 6 (`Parametres.taux_recours_garantie`, et son
   jumeau de `moteur/js/config.js`) ; un taux à part pour l'ASPA que l'effet
   retour chiffre aux scénarios 2 à 5, qui garde la moitié de la DREES ; les
   tests qui tiennent 0,5 (`test_affirmations.py`,
   `test_controle_drees_panorama.py`, `test_cout.py`),
   `scripts/garantie_par_sexe.py`, et le texte qui dit le recours
   (`pages.js`, vers les lignes 13126 et 13456). Puis, si le propriétaire le
   veut, la garantie qui voit la réversion gardée.
4. **Le stock au simulateur** : un assuré mort avant la bascule laisse à son
   conjoint, au scénario 6, la réversion que le scénario 1 lui sert
   (`droit/reversion.js`, rattachée à la comparaison dans `simulateur.js`) ;
   mort après, rien tant que l'étape 5 n'est pas faite. Le bloc de la
   réversion du simulateur (« Dans les systèmes 2, 3 et 4, aucune
   réversion », vers la ligne 6725 de `pages.js`) le dit.
5. **La rente sur deux têtes et sa démonstration** (décisions 17 à 19, 21,
   23, 24, 26, 27), sans doute en deux sessions. Au simulateur, à la
   liquidation au scénario 6 : par défaut pour un marié déclaré, sur demande
   pour un pacsé ou un concubin, la pension baisse du prix actuariel d'une
   rente de 50 % au survivant, sur l'âge réel des deux conjoints et les
   tables de génération par sexe ; la renonciation signée des deux. Les
   tests démontrent la propriété du propriétaire, qu'aucun choix d'un couple
   ne fait payer les autres cotisants ni l'impôt : la valeur actuelle de la
   baisse égale celle de la rente, au prix d'équilibre de la caisse des
   rentes de survivant, et le prix recalculé chaque année reporte tout écart
   sur les couples qui la paient. Au coût, rien de public (le système G de
   l'étude, 0,82 point brut, celui de l'étape 1). Puis l'épargne au nom du
   conjoint après la liquidation (remariage, demande tardive), et le divorce,
   la rente payée restant à l'ex-conjoint.
6. **Le décès d'un actif** (décisions 22, 25, 27) : la moitié de son compte
   notionnel passe au compte du conjoint, convertie tout de suite au
   diviseur de son âge s'il a des enfants à charge, sinon touchée avec sa
   propre retraite. Au simulateur d'abord, puis au coût (l'étude : 6,6 Md€
   de capital en 2026), en regardant ce que le diviseur doit aujourd'hui aux
   comptes des morts.
7. **Le README et le texte du site** pour ce que les étapes 4 à 6 ajoutent.
