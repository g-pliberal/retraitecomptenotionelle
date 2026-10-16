# Étape 7, sixième partie : la fécondité et les migrations de la page Coût, au modèle

**La demande.** Vague bis du 16 octobre 2026, session 3 : le point 1 de « Ce
qui reste » de la cinquième partie (note du 16 octobre, « variantes dans les
pages ») — les variantes de fécondité et de migrations de la page Coût, au
modèle. Leur affichage revient à une session des pages ; la mortalité
différentielle et les départs qui suivent l'espérance de vie n'en étaient
pas. Ni `pages.js` ni la saisie ne sont touchés.

**Ce que la source publie, lu le jour même.** Sur la page
https://www.insee.fr/fr/statistiques/8990856, de même disposition que le
central : `11_fec_haute.xlsx` et `12_fec_basse.xlsx` (1,70 et 1,20 enfant par
femme, au lieu de 1,45), `15_smi_haut.xlsx` et `16_smi_bas.xlsx` (+ 230 000 et
+ 70 000 par an, au lieu de + 150 000). Les noms en `_haute` et `_basse` des
migrations n'existent pas (erreur 500). Sous la fécondité, la pyramide des 50
ans et plus est celle du central à l'unité, chaque année jusqu'en 2070 ; les
20-64 ans n'en diffèrent qu'à partir de 2046 : 36,42 et 31,83 millions en
2070, contre 34,08. Sous les migrations, la pyramide diffère dès le 1er
janvier 2024 : 21,69 et 20,48 millions de 65 ans et plus en 2070, contre
21,08 ; 37,32 et 30,84 millions de 20-64 ans.

**Ce qui est fait.**

- *Le récupérateur* (`insee_projections_population.py`) lit les six
  classeurs d'une seule composante, et le central, en ligne ou d'un dossier
  (`--dossier`, qui remplace `--variantes`) ; il vérifie que la pyramide de
  la fécondité est celle du central (et ne l'écrit pas), que chaque basse
  compte moins de 20-64 ans que sa haute (dès 2047 pour la fécondité), moins
  de 65 ans et plus sous les migrations basses ; il refait les arrivées
  tardives sur le classeur de chaque migration.
- *La certification* ajoute les migrations à `population_par_age_variantes.csv`
  (4 950 effectifs de plus), les quatre scénarios à
  `population_active_variantes.csv` (180), et écrit
  `arrivees_tardives_variantes.csv` (260 valeurs), de 2026 à 2070 comme les
  autres variantes. `sources.yaml` et la ligne des limites le disent.
- *La pyramide* : `Population(racine, hypothese_esperance_vie, demographie)`,
  `demographie` parmi `VARIANTES_DEMOGRAPHIQUES` ; la fécondité ne remplace
  que les 20-64 ans, les migrations les deux séries. Deux composantes
  croisées, que l'INSEE ne publie pas, sont refusées (`verifier_demographie`).
  `facteur_actifs(annee)` : les 20-64 ans de la variante sur ceux du central.
  `ArriveesTardives` et `CarrieresIncompletes` prennent la variante : le
  manque des arrivées est celui de son classeur, le facteur des natifs reste
  tiré du central, les durées du COR comptant les arrivées du central.
- *La page Coût* : `memoire.cout(parametres, demographie=...)`, la clé du
  central inchangée ; la grille simulée est partagée, ses complétudes refaites
  sur la variante (`_sous_la_demographie`). Dans `_avenir`, la dépense du COR
  se multiplie par ce que la pyramide de la variante, ses arrivées comprises,
  change à la masse du système actuel (`facteur_pyramide`, qui remplace
  `facteur_esperance_vie`), et le PIB par ce qu'elle change aux 20-64 ans
  (`facteur_pib`), l'emploi du COR, qui projette le PIB, suivant le central ;
  le bilan divise la dépense du COR, en part de PIB, par le second. Les
  ressources, en part de PIB, ne bougent pas.
- *Les variantes d'espérance de vie suivent aussi le PIB*, la même règle
  valant pour toutes : leurs 20-64 ans bougent de −0,6 et +0,4 % en 2070, et
  le système actuel passe de 14,05 et 16,61 % du PIB à 14,14 et 16,54 %, plus
  près du COR (14,30 et 16,35 %). Le tableau de la page Coût en bouge de
  quelques centièmes, à la prochaine régénération.
- *Les tests* : la pyramide sous la fécondité et les migrations, les
  arrivées, le refus des composantes croisées (`test_donnees.py`) ; la page
  Coût sous les quatre variantes, contre le COR à trois dixièmes près, rien
  ne bougeant avant 2026 que les arrivées de 2024 et 2025 (`test_cout.py`).
- *Le registre* : les trois points « variantes démographiques » (destinie_2,
  trajectoire, retraites_cor2026) passent à `repris` ; le point du rapport du
  COR (fig. 2.18 à 2.20) dit la mesure.
- *Le parcours de présentation* suit les comptes de la page Données :
  142 133 valeurs, 169 séries.

**Ce que la variante déplace, mesuré le jour même**, en part de PIB, dépense
du bilan, sous les réglages de la page (basse / centrale / haute) :

| | 2050 | 2070 | solde 2070 | solde moyen |
|---|---|---|---|---|
| Fécondité, système actuel | 14,44 / 14,37 / 14,26 | 16,38 / 15,30 / 14,31 | −3,47 / −2,39 / −1,40 | −1,39 / −1,13 / −0,88 |
| Fécondité, proposition | 9,76 / 9,71 / 9,64 | 8,70 / 8,12 / 7,60 | −0,53 / +0,05 / +0,57 | −1,17 / −1,02 / −0,88 |
| Migrations, système actuel | 15,02 / 14,37 / 13,77 | 16,54 / 15,30 / 14,27 | −3,63 / −2,39 / −1,36 | −1,77 / −1,13 / −0,57 |
| Migrations, proposition | 10,16 / 9,71 / 9,30 | 8,82 / 8,12 / 7,55 | −0,65 / +0,05 / +0,62 | −1,42 / −1,02 / −0,67 |

Le COR publie, en 2070, 16,34 et 14,34 % sous la fécondité, 16,40 et 14,16 %
sous les migrations (rapport annuel de 2026, fig. 2.18 à 2.20) : le modèle y
est à quatre centièmes et à quatorze centièmes près. Le rapport de
dépendance passe, en 2070, de 0,619 à 0,662 et 0,579 sous la fécondité, à
0,664 et 0,581 sous les migrations.

*La proposition ne s'en protège pas comme de la longévité.* Son diviseur
absorbe trois ans d'espérance de vie ; il ne voit pas qui cotise. Sous la
fécondité, ses pensions sont les mêmes euros sur un PIB qui bouge de ±7 % en
2070 : sa dépense et son solde bougent d'un demi-point. C'est en partie un
effet de convention : ses comptes et ses pensions s'indexent sur la masse
salariale du central (`limites/5-ter-trajectoire.md`), quand une fécondité ou
des migrations plus fortes la feraient croître plus vite, et rendraient aux
comptes une part de ce que le PIB gagne.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'affichage*, par la session des pages : le tableau de la page Coût
   généralisé aux trois composantes (une table figée par composante, comme
   `figer_esperance_vie`, du `memoire.cout(demographie=...)` de chaque
   variante). Le réglage du simulateur n'a pas à suivre.
2. *L'indexation sous la variante* : la masse salariale de la variante, au
   lieu de celle du central, pour les comptes et les pensions de la
   proposition — elle toucherait le simulateur, non le diviseur.
3. *La mortalité différentielle* des cas types, *les départs qui suivent
   l'espérance de vie*, *la queue observée* de 85 à 98 ans, *2025* sous la
   loi seule : inchangés.
4. *Au propriétaire*, toujours : si le rapport de dépendance sous chaque
   variante doit s'écrire sur la page.
