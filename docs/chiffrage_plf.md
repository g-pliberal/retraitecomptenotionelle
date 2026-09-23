# Chiffrage budgétaire de la proposition, pour un projet de loi de finances

**Tous les tableaux de ce document sont écrits par
`python scripts/chiffrage_plf.py`, qui les recalcule depuis le modèle.** Ne pas
les modifier à la main : `tests/test_prose.py` refuse un document qui ne serait
plus celui que le script produit. La prose, elle, est datée du
22 septembre 2026 et relève du régime `recit` de `docs/fraicheur.md` : elle
raconte ce que ces chiffres voulaient dire ce jour-là. Elle a été corrigée le
23 septembre 2026 là où elle nommait mal ce qu'elle chiffrait — un « solde
public » qui n'était que celui de la retraite, des « prélèvements
obligatoires » qui comptaient des dépenses de l'État —, et chaque correction
le dit à sa place.

La série annuelle complète, année par année et pour les deux variantes, est
dans `docs/chiffrage_plf.csv` — séparateur `;`, virgule décimale, ouvrable
directement dans un tableur français.

## Ce que ce document chiffre

Le scénario 6 du dépôt, c'est-à-dire la proposition du Parti libéral français :
taux unique de 18 % en répartition à compter de la bascule, 5 % de
capitalisation obligatoire prélevés en plus sur la même assiette, et une
garantie vieillesse de 800 € par personne (plus 250 € d'allocation
d'isolement), individualisée, financée par l'impôt, qui remplace l'ASPA et tous
les minima de pension.

*Ajouté le 23 septembre 2026.* Et une **TVA à taux unique de 19,7 %**,
décidée ce jour-là : les quatre taux d'aujourd'hui — 20, 10, 5,5 et 2,1 % —
cèdent la place à un seul, et ce qu'il rapporte de plus va à la retraite de la
proposition, à sa garantie vieillesse d'abord, à son régime ensuite. Le taux
est celui qui couvre chaque année le déficit de la variante rétroactive,
garantie comprise, sans emprunter : celui du pic de 2048, 19,69 % exactement,
arrondi au dixième. Il reste sous les 20 % du taux normal parce qu'il supprime
les taux réduits, qui coûtent 52 Md€ nets par an. Tous les tableaux la
portent ; avant elle, le fait central affichait un écart de -1,44 point de PIB.

*Ajouté le même jour, le soir.* Et un **âge légal de départ de 65 ans** à
compter de la bascule : toute pension que la proposition liquide l'est à cet
âge au plus tôt, et qui serait parti avant travaille et cotise jusque-là. Le
taux de TVA a été fixé d'abord à 21,1 %, par la même règle, avant que la
proposition ne prenne cet âge ; celui-ci fait cotiser davantage et servir
moins de pensions, et la même règle donne alors 19,7 %. Elle le donne en
supposant, comme la page Coût, que ceux que le report fait attendre sont en
emploi : si la moitié seulement l'étaient, il faudrait 20,3 %.

**Deux variantes sont chiffrées, et l'écart entre elles est le premier fait
budgétaire du dossier.**

- **Rétroactive** — la convention par défaut du dépôt, celle que le site
  affiche : toutes les pensions, y compris celles déjà liquidées, sont
  recalculées en comptes notionnels depuis 1941.
- **Prospective** — les droits acquis sont figés à la bascule, débarrassés des
  avantages non contributifs et convertis en capital ; les pensions déjà
  liquidées ne bougent pas. C'est la variante juridiquement soutenable, et
  `scripts/proposition_prospective.py` dit pourquoi. *Précisé le 23 septembre
  2026* : ce sont les pensions de DROIT DIRECT déjà liquidées qui ne bougent
  pas ; les pensions de réversion en cours de service cessent à la bascule,
  comme dans toutes les variantes notionnelles (hypothèse n° 9), et c'est
  1,45 point de PIB de dépense en moins dès 2026. La phrase le taisait.

## Conventions de lecture

- Les grandeurs sont en **points de PIB** — l'unité du COR, et la seule où
  l'année de la bascule et 2070 se comparent sans convention d'actualisation.
  Les montants entre parenthèses sont des **milliards d'euros courants**.
- **Le PIB n'est publié que jusqu'en 2025.** Au-delà, il est projeté au rythme
  nominal du COR composé avec sa trajectoire d'emploi, qui recule d'ici 2070.
  Les euros des années lointaines portent donc une hypothèse de croissance, que
  les points de PIB ne portent pas. C'est pourquoi les deux sont donnés.
- **Pensions** : la dépense de pensions du régime. Les scénarios notionnels ne
  servent aucune pension de réversion — voir l'hypothèse n° 9.
- **Garantie nette** : la garantie vieillesse, financée par l'impôt et comptée
  hors du compte des cotisants, moins ce que les successions en reprennent.
- **Solde régime** : recettes moins dépenses du régime seul.
- **TVA** (*ajouté le 23 septembre 2026*) : ce que la TVA à taux unique
  rapporte de plus que les quatre taux d'aujourd'hui, sur les assiettes que
  publie la DG Trésor (Trésor-Éco n° 371), tenues à leur part de PIB de 2025.
  Elle paie d'abord la garantie nette, et entre au régime pour le reste :
  « Recettes » la compte en entier, « Solde régime » est pris après la
  garantie, et « Solde + garantie » ne retranche plus que la part de la
  garantie qu'elle ne couvre pas — aucune, à 19,7 %. C'est pourquoi les deux
  soldes sont égaux dans les tableaux A à D.
- **Solde + garantie** : le précédent, diminué de la garantie que le
  contribuable porte. **Ce n'est pas un solde toutes administrations
  publiques**, et l'hypothèse n° 1 dit exactement pourquoi.
- **Rappel sc. 1** : le solde du système actuel, même année, même périmètre — le
  compte du COR, qui consolide dépenses et ressources de l'ensemble des régimes
  légalement obligatoires, fonds de solidarité vieillesse compris.
- **Écart** : « Solde + garantie » moins « Rappel sc. 1 ». Négatif, la
  proposition dégrade le solde de la retraite, garantie comprise, par rapport
  au droit en vigueur. *Corrigé le 23 septembre 2026* : le document l'appelait
  « écart de solde public », et ce n'en est pas un. Une part des recettes que
  la retraite perd sont des versements d'autres administrations — la
  contribution d'équilibre de l'État employeur, ses subventions, la branche
  famille —, qui sont autant de dépenses que leur payeur cesse de faire : au
  niveau des administrations publiques consolidées, ils s'annulent. Le fait
  central les isole ; le document ne chiffre pas le solde consolidé, faute de
  séparer, dans les cotisations, ce que paient les employeurs publics.
- La pondération est celle du dépôt : chaque cas type porte l'effectif de
  retraités de sa caisse dans les masses de pensions, et ses cotisants dans les
  masses de cotisations.

## Le fait central

<!-- fait_central:debut -->
| En 2026 | Points de PIB | Milliards d'euros |
|---|---:|---:|
| Recettes retirées au système de retraite | -5,80 | -178 |
| dont cotisations, au taux unique | -1,40 | -43 |
| dont impôts et taxes affectés | -2,14 | -66 |
| dont versements de l'État et de la branche famille | -2,26 | -69 |
| TVA à taux unique de 19,7 %, affectée à la retraite | +1,63 | +50 |
| Dépense publique retirée (pensions et garantie) | -4,89 | -150 |
| **Écart de solde de la retraite, garantie comprise, variante rétroactive** | **+0,72** | **+22** |
| **Écart de solde de la retraite, garantie comprise, variante prospective** | **-2,43** | **-75** |
<!-- fait_central:fin -->

La proposition retire à la fois des recettes et de la dépense, et **elle en
retire plus du côté des recettes**. C'est le résultat que tout le reste du
document décline : une dépense de pensions qui baisse de plus d'un tiers ne suffit pas
à compenser des prélèvements qui baissent davantage.

*Corrigé le 23 septembre 2026.* La dernière phrase est fausse, et la
décomposition des recettes, ajoutée ce jour-là au tableau, le montre : ce que
les ménages et les entreprises cessent de payer — les cotisations et les impôts
affectés — baisse MOINS que la dépense. Ce qui fait passer les recettes
retirées au-dessus de la dépense retirée, ce sont les versements de l'État et
de la branche famille, que la retraite ne reçoit plus et que leurs payeurs
gardent. Le déficit que la proposition creuse est donc celui du système de
retraite, et le solde public consolidé s'en écarte, dans le sens favorable à
la proposition, d'une somme du même ordre — moins la part du taux unique que
l'État paierait comme employeur, qui est dans les cotisations.

*Ajouté le 23 septembre 2026, avec la TVA à taux unique.* Le tableau a changé
de signe dans la variante rétroactive. La TVA apporte, à trois centièmes de
point près, ce que les impôts affectés supprimés apportaient : la proposition
ne renonce plus à cette recette, elle en **change l'assiette**, de la CSG, de
la taxe sur les salaires, du forfait social et de la C3S vers la
consommation. Ce qui reste, c'est une dépense qui baisse davantage que les
cotisations et les versements publics réunis. La variante prospective, elle,
demeure en déficit : 21,1 % ne la couvrait pas, et il lui aurait fallu 28,2 %
la première année. Avec l'âge légal de 65 ans, il lui faudrait 26,5 %, et
19,7 % la laisse en déficit jusqu'en 2062.

## Les quatre arbitrages qui déplacent le chiffrage

Aucun de ces quatre points n'est tranché par le programme écrit. Deux d'entre
eux — les impôts affectés et la rétroactivité — valent chacun, à eux seuls,
plus que l'écart de solde que le tableau précédent affiche.

*Ajouté le 23 septembre 2026.* Une cinquième ligne dit ce que vaut la TVA à
taux unique, décidée ce jour-là : y renoncer ramène la variante rétroactive à
l'écart d'avant elle. Et le coefficient d'équilibre, calculé avec elle, dépasse
un : il ne dit plus de combien il faudrait rogner les pensions, mais de combien
l'excédent permettrait de les relever — ce que personne ne propose.

<!-- arbitrages:debut -->
| Arbitrage ouvert | Ce qu'il déplace en 2026 | En milliards |
|---|---:|---:|
| Impôts et taxes affectés, si l'État continue de les lever | +2,14 pt | +66 |
| Subventions d'équilibre, même question | +0,25 pt | +8 |
| Renoncer à la rétroactivité (variante prospective) | -3,15 pt | -97 |
| Renoncer à la TVA à taux unique de 19,7 % | -1,63 pt | -50 |
| Appliquer le coefficient d'équilibre, non appliqué ici | 1,06 sur toutes les pensions | soit 6,3 % de plus |
<!-- arbitrages:fin -->

## Tableaux annuels

### A. Variante rétroactive — trajectoire annuelle

<!-- annuel_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 8,80 (270) | 0,44 (14) | 9,24 (283) | 9,80 (300) | +0,55 (+17) | +0,55 (+17) | -0,16 (-5) | +0,72 |
| 2027 | 8,76 (275) | 0,43 (14) | 9,19 (289) | 9,98 (314) | +0,79 (+25) | +0,79 (+25) | -0,22 (-7) | +1,01 |
| 2028 | 8,69 (281) | 0,42 (13) | 9,10 (294) | 10,11 (327) | +1,00 (+32) | +1,00 (+32) | -0,24 (-8) | +1,24 |
| 2029 | 8,62 (287) | 0,40 (13) | 9,02 (300) | 10,13 (337) | +1,12 (+37) | +1,12 (+37) | -0,17 (-6) | +1,29 |
| 2030 | 8,77 (301) | 0,39 (13) | 9,15 (314) | 10,13 (347) | +0,98 (+33) | +0,98 (+33) | -0,20 (-7) | +1,18 |
| 2031 | 8,97 (317) | 0,37 (13) | 9,34 (330) | 10,01 (353) | +0,67 (+24) | +0,67 (+24) | -0,24 (-9) | +0,91 |
| 2032 | 9,04 (329) | 0,36 (13) | 9,40 (342) | 10,05 (365) | +0,65 (+24) | +0,65 (+24) | -0,26 (-10) | +0,91 |
| 2033 | 9,05 (339) | 0,34 (13) | 9,40 (352) | 10,07 (377) | +0,67 (+25) | +0,67 (+25) | -0,27 (-10) | +0,94 |
| 2034 | 9,18 (353) | 0,33 (13) | 9,51 (366) | 10,05 (387) | +0,54 (+21) | +0,54 (+21) | -0,34 (-13) | +0,88 |
| 2035 | 9,26 (366) | 0,31 (12) | 9,58 (379) | 10,06 (398) | +0,48 (+19) | +0,48 (+19) | -0,38 (-15) | +0,86 |
| 2036 | 9,35 (379) | 0,30 (12) | 9,65 (392) | 10,06 (408) | +0,41 (+17) | +0,41 (+17) | -0,43 (-17) | +0,84 |
| 2037 | 9,44 (393) | 0,29 (12) | 9,72 (405) | 10,08 (420) | +0,36 (+15) | +0,36 (+15) | -0,49 (-20) | +0,84 |
| 2038 | 9,52 (407) | 0,27 (12) | 9,79 (418) | 10,06 (430) | +0,27 (+12) | +0,27 (+12) | -0,53 (-23) | +0,80 |
| 2039 | 9,59 (421) | 0,26 (11) | 9,85 (432) | 10,04 (441) | +0,19 (+8) | +0,19 (+8) | -0,57 (-25) | +0,76 |
| 2040 | 9,65 (434) | 0,25 (11) | 9,90 (445) | 10,04 (452) | +0,14 (+6) | +0,14 (+6) | -0,61 (-27) | +0,75 |
<!-- annuel_retroactif:fin -->

### B. Variante rétroactive — horizon long

<!-- horizon_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 9,83 (498) | 0,19 (10) | 10,03 (507) | 10,07 (510) | +0,04 (+2) | +0,04 (+2) | -0,89 (-45) | +0,93 |
| 2050 | 9,87 (555) | 0,16 (9) | 10,03 (564) | 10,06 (566) | +0,03 (+2) | +0,03 (+2) | -1,22 (-68) | +1,25 |
| 2055 | 9,69 (603) | 0,14 (9) | 9,83 (612) | 10,05 (625) | +0,22 (+13) | +0,22 (+13) | -1,54 (-96) | +1,75 |
| 2060 | 9,27 (638) | 0,14 (9) | 9,41 (648) | 10,04 (691) | +0,63 (+44) | +0,63 (+44) | -1,77 (-122) | +2,40 |
| 2065 | 8,79 (667) | 0,14 (10) | 8,92 (677) | 10,04 (763) | +1,12 (+85) | +1,12 (+85) | -2,11 (-160) | +3,23 |
| 2070 | 8,24 (688) | 0,14 (12) | 8,38 (700) | 10,14 (847) | +1,76 (+147) | +1,76 (+147) | -2,39 (-200) | +4,15 |
<!-- horizon_retroactif:fin -->

### C. Variante prospective — trajectoire annuelle

<!-- annuel_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 12,16 (373) | 0,24 (7) | 12,39 (380) | 9,80 (300) | -2,60 (-80) | -2,60 (-80) | -0,16 (-5) | -2,43 |
| 2027 | 12,07 (380) | 0,24 (7) | 12,31 (387) | 9,98 (314) | -2,33 (-73) | -2,33 (-73) | -0,22 (-7) | -2,11 |
| 2028 | 11,88 (384) | 0,23 (8) | 12,11 (392) | 10,11 (327) | -2,01 (-65) | -2,01 (-65) | -0,24 (-8) | -1,77 |
| 2029 | 11,69 (389) | 0,23 (8) | 11,92 (397) | 10,13 (337) | -1,79 (-60) | -1,79 (-60) | -0,17 (-6) | -1,62 |
| 2030 | 11,80 (404) | 0,23 (8) | 12,02 (412) | 10,13 (347) | -1,90 (-65) | -1,90 (-65) | -0,20 (-7) | -1,70 |
| 2031 | 11,98 (423) | 0,22 (8) | 12,20 (431) | 10,01 (353) | -2,19 (-77) | -2,19 (-77) | -0,24 (-9) | -1,95 |
| 2032 | 11,98 (436) | 0,22 (8) | 12,20 (444) | 10,05 (365) | -2,15 (-78) | -2,15 (-78) | -0,26 (-10) | -1,89 |
| 2033 | 11,91 (446) | 0,22 (8) | 12,13 (454) | 10,07 (377) | -2,06 (-77) | -2,06 (-77) | -0,27 (-10) | -1,79 |
| 2034 | 11,98 (461) | 0,21 (8) | 12,19 (469) | 10,05 (387) | -2,14 (-82) | -2,14 (-82) | -0,34 (-13) | -1,80 |
| 2035 | 11,99 (474) | 0,21 (8) | 12,19 (482) | 10,06 (398) | -2,14 (-84) | -2,14 (-84) | -0,38 (-15) | -1,75 |
| 2036 | 12,00 (487) | 0,20 (8) | 12,21 (495) | 10,06 (408) | -2,15 (-87) | -2,15 (-87) | -0,43 (-17) | -1,72 |
| 2037 | 12,03 (501) | 0,20 (8) | 12,23 (509) | 10,08 (420) | -2,15 (-89) | -2,15 (-89) | -0,49 (-20) | -1,66 |
| 2038 | 12,04 (515) | 0,19 (8) | 12,23 (523) | 10,06 (430) | -2,17 (-93) | -2,17 (-93) | -0,53 (-23) | -1,64 |
| 2039 | 12,05 (528) | 0,18 (8) | 12,23 (537) | 10,04 (441) | -2,19 (-96) | -2,19 (-96) | -0,57 (-25) | -1,61 |
| 2040 | 12,03 (541) | 0,18 (8) | 12,21 (549) | 10,04 (452) | -2,17 (-98) | -2,17 (-98) | -0,61 (-27) | -1,56 |
<!-- annuel_prospectif:fin -->

### D. Variante prospective — horizon long

<!-- horizon_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 11,88 (601) | 0,15 (8) | 12,03 (609) | 10,07 (510) | -1,96 (-99) | -1,96 (-99) | -0,89 (-45) | -1,07 |
| 2050 | 11,56 (650) | 0,13 (7) | 11,70 (657) | 10,06 (566) | -1,64 (-92) | -1,64 (-92) | -1,22 (-68) | -0,42 |
| 2055 | 11,05 (688) | 0,12 (8) | 11,17 (695) | 10,05 (625) | -1,12 (-70) | -1,12 (-70) | -1,54 (-96) | +0,42 |
| 2060 | 10,31 (710) | 0,12 (8) | 10,43 (718) | 10,04 (691) | -0,39 (-27) | -0,39 (-27) | -1,77 (-122) | +1,37 |
| 2065 | 9,55 (725) | 0,12 (9) | 9,68 (735) | 10,04 (763) | +0,37 (+28) | +0,37 (+28) | -2,11 (-160) | +2,48 |
| 2070 | 8,76 (732) | 0,13 (11) | 8,89 (743) | 10,14 (847) | +1,25 (+104) | +1,25 (+104) | -2,39 (-200) | +3,64 |
<!-- horizon_prospectif:fin -->

### E. Prélèvements retraite, avant et après, et ce que l'État verse à part

<!-- prelevements:debut -->
| Année | Cotisations (sc. 1) | Impôts et taxes affectés (sc. 1) | **Prélèvements sc. 1** | Cotisations 18 % (sc. 6) | Pilier obligatoire 5 % (sc. 6) | TVA 19,7 % (sc. 6) | **Prélèvements sc. 6** | Écart | Versé par l'État au sc. 1, hors prélèvements |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 9,16 (281) | 2,14 (66) | **11,30 (346)** | 7,76 (238) | 2,16 (66) | 1,63 (50) | **11,55 (354)** | +0,25 | 1,88 (58) |
| 2030 | 9,10 (312) | 2,13 (73) | **11,23 (385)** | 8,10 (278) | 2,25 (77) | 1,63 (56) | **11,98 (411)** | +0,75 | 1,87 (64) |
| 2035 | 8,93 (353) | 2,08 (82) | **11,01 (435)** | 8,04 (318) | 2,23 (88) | 1,63 (64) | **11,90 (470)** | +0,88 | 1,84 (73) |
| 2040 | 8,81 (397) | 2,06 (93) | **10,87 (489)** | 8,02 (361) | 2,23 (100) | 1,63 (73) | **11,88 (534)** | +1,00 | 1,81 (82) |
| 2050 | 8,63 (485) | 2,01 (113) | **10,64 (598)** | 8,05 (453) | 2,24 (126) | 1,63 (92) | **11,92 (670)** | +1,28 | 1,77 (100) |
| 2060 | 8,51 (586) | 1,99 (137) | **10,50 (722)** | 8,04 (553) | 2,23 (154) | 1,63 (112) | **11,90 (819)** | +1,40 | 1,75 (120) |
| 2070 | 8,47 (708) | 1,98 (165) | **10,45 (873)** | 8,14 (680) | 2,26 (189) | 1,63 (136) | **12,03 (1 005)** | +1,58 | 1,74 (146) |
<!-- prelevements:fin -->

*Corrigé le 23 septembre 2026.* Le tableau comptait jusque-là, parmi les
prélèvements du système actuel, la contribution d'équilibre de l'État employeur
et ses subventions d'équilibre, et affichait un écart de prélèvements de près
de trois points et demi. Ce sont des dépenses de son budget, financées par
l'impôt général, et la comptabilité nationale ne range pas la première — une
cotisation *imputée* — parmi les prélèvements obligatoires. Elles sont
désormais dans une colonne à part, hors des totaux et de l'écart.

Le pilier obligatoire n'est pas une recette publique : il constitue un capital
au nom de chacun, hors du compte de la répartition. Il figure ici parce qu'un
projet de loi de finances raisonne en taux de prélèvements obligatoires, et que
la proposition rend ces cinq points obligatoires. Les cinq points de
capitalisation **volontaire** n'y sont pas : ils ne sont pas imposés, et le
salaire net affiché par le simulateur est celui qui les laisse au salarié.

### F. Agrégats sur la projection

<!-- agregats:debut -->
| Sur 2026-2070 | Rétroactive | Prospective | Système actuel |
|---|---:|---:|---:|
| Dépense de pensions cumulée, Md € constants de 2026 | 15 094 | 18 023 | 23 442 |
| Écart de dépense au système actuel | -8 348 | -5 419 | — |
| Garantie vieillesse brute cumulée | 534 | 411 | — |
| Reprises sur succession | -188 | -156 | — |
| Garantie nette cumulée | 345 | 255 | — |
| Solde moyen, points de PIB | +0,54 | -1,27 | -1,13 |
| Dette accumulée en 2070, points de PIB | -33 | +97 | +66 |
| Première année d'équilibre | 2026 | 2063 | jamais |
<!-- agregats:fin -->

La variante rétroactive ne fait pas mieux que le droit en vigueur sur la
moyenne de la projection : elle est meilleure après le milieu du siècle, pire
avant, et le stock de dette qu'elle accumule d'ici 2070 dépasse celui du
système actuel. La variante prospective en accumule plusieurs fois plus.

*Corrigé le 23 septembre 2026, avec la TVA à taux unique.* Le paragraphe
précédent décrit le chiffrage sans TVA. Avec elle, la variante rétroactive est
en excédent chaque année sauf 2044 et 2045, où il lui manque six et trois
millièmes de point de PIB — le taux exact du pic est 21,12 % —, et elle
accumule d'ici 2070 des réserves, non une dette. La variante prospective reste
en déficit jusqu'en 2061 et accumule encore une dette, moins de la moitié de
celle d'avant la TVA.

*Corrigé le 23 septembre 2026 au soir, avec l'âge légal de 65 ans et la TVA
ramenée à 19,7 %.* La variante rétroactive est à l'équilibre ou en excédent
chaque année, au plus juste en 2048, où le taux exact est de 19,69 %, et elle
aborde 2070 avec des réserves d'un tiers du PIB. La variante prospective, à qui
le taux n'est pas ajusté, reste en déficit de 2026 à 2062, et sa dette atteint
97 % du PIB en 2070, au-dessus de celle du système actuel.

*Corrigé le 23 septembre 2026.* Les deux premières lignes cumulaient la
dépense que le modèle projette lui-même, plus haute que celle du COR de trois
points de PIB en 2070, quand les tableaux A à D, le solde moyen et la dette
portent celle du COR. L'économie en était surestimée d'environ 9 % : 9 036
milliards au lieu de 8 285 pour la variante rétroactive. Toutes les lignes
sont désormais sur la même base.

## La pondération du recensement

Elle n'intervient qu'à un endroit, et elle y vaut un cinquième du coût de la
garantie vieillesse. La garantie sert deux planchers — 800 € par personne,
1 050 € pour qui vit seul — et l'enquête sur les pensions ne dit pas avec qui
l'on vit. Le recensement le dit, lui, âge par âge et par sexe. Pesé sur les
années vécues après 65 ans, et avec la table de mortalité du **premier
vingtile** — celle des bénéficiaires, qui meurent plus tôt et pèsent donc moins
les grands âges, ceux où l'on vit seul —, il donne une proportion de femmes
ne vivant pas en couple près du double de celle des hommes, et les deux planchers se
mélangent dans cette proportion, sexe par sexe.

`docs/limites.md`, section « Le scénario 6, et ce que sa garantie ne voit pas »,
porte le tableau des trois conventions et ce que le passage de l'une à l'autre
déplace. La même pondération sert aux reprises sur succession. Les tableaux
ci-dessus sont tous pris sous cette pondération.

## Les hypothèses fragiles, par ordre d'enjeu budgétaire

### 1. Les impôts et taxes affectés sortent du système, et le programme ne dit pas ce qu'ils deviennent

**C'est le plus gros arbitrage du dossier, et il n'est pas tranché.** Le modèle
ne reconduit pas les impôts et taxes affectés — CSG vieillesse, taxe sur les
salaires, forfait social, C3S — dans les ressources du système. L'argument est
juste du point de vue du régime : un compte notionnel ne crédite que ce qui est
assis sur un revenu d'activité, et un impôt affecté n'ouvre de droit à
personne. Mais il ne dit pas si l'État **cesse de lever** ces impôts ou les
**affecte ailleurs**.

- S'il les supprime, la colonne « Solde + garantie » des tableaux A et B est la
  bonne.
- S'il les conserve pour d'autres dépenses, le solde consolidé des
  administrations publiques est meilleur de ce que le tableau des arbitrages
  chiffre, et la lecture du dossier change de signe la première année.

Même remarque, plus petite, pour les subventions d'équilibre : la fusion des
régimes supprime l'objet de la subvention — il n'y a plus de retraité sans
cotisants dès lors qu'il n'y a plus qu'un régime —, mais pas la dépense. Les
pensions de la SNCF, des mines et des marins restent servies, portées par les
cotisants du régime unifié, et le modèle le fait bien.

*Ajouté le 23 septembre 2026.* Le solde consolidé est meilleur, en outre, de
ce que l'État employeur et la branche famille cessent de verser à la retraite :
la contribution d'équilibre, qui couvre les pensions des fonctionnaires de
l'État, et l'assurance vieillesse des parents au foyer. Le fait central les
isole, avec les subventions : ce ne sont pas des impôts qu'on lève ou qu'on
abandonne, mais des dépenses que leur payeur ne fait plus. Moins, pour l'État,
sa part d'employeur du taux unique, que le modèle ne sépare pas des autres
cotisations.

Rien ne devrait être déposé avant que ce point soit écrit.

*Ajouté le 23 septembre 2026.* La TVA à taux unique ne tranche pas cette
question. Elle remplace ces impôts dans les ressources de la retraite, mais ne
dit pas si l'État cesse de les lever : s'il les lève encore, la proposition
prélève les deux, et la moitié rendue aux salaires (`restitution.py`) ne rend
qu'une partie de ce que la TVA prend.

### 2. La variante par défaut est rétroactive, donc elle suppose une loi rétroactive

Le scénario 6 du dépôt recalcule toutes les pensions depuis 1941, **y compris
celles déjà liquidées**, et c'est de là que vient l'essentiel de l'économie de
dépense du tableau A. Les pensions liquidées sont des situations légalement
acquises : c'est la mesure la plus exposée du dossier, devant le Conseil
constitutionnel comme au Parlement. Le tableau des arbitrages chiffre ce que
coûte d'y renoncer, et les tableaux C et D donnent la trajectoire complète de la
variante prospective. Un projet de loi de finances ne peut chiffrer que la
seconde, sauf à assumer la première explicitement.

### 3. Aucune règle de pilotage n'est appliquée

Un système notionnel réel porte un coefficient d'équilibre qui multiplie toutes
les pensions par un même facteur : il vaut un quand l'année tombe juste, moins
de un quand il faut rogner. Le modèle le **calcule** — le tableau des
arbitrages le donne pour l'année de la bascule — mais ne l'**applique pas** :
les trajectoires ci-dessus sont celles d'un système qui ne se pilote pas. Le
déficit affiché et la baisse de pension qu'un pilotage imposerait sont donc
**deux lectures du même manque, et il ne faut pas les additionner**. Le facteur
étant commun à toutes les pensions, l'appliquer déplacerait les niveaux sans
toucher aux écarts entre carrières.

*Ajouté le 23 septembre 2026.* La TVA à taux unique tient lieu de ce
pilotage : elle comble le manque que le coefficient aurait rogné. Elle ne se
pilote pas pour autant — son taux est fixe, et le déficit qu'elle comble
culmine en 2044 puis se résorbe —, si bien que la variante rétroactive dégage
ensuite des excédents que rien, dans le modèle, n'emploie.

### 4. L'écart avec le COR à l'horizon 2070 n'est pas résolu

Le COR projette la même grandeur avec un modèle de population complet et une
méthode qui n'a rien de commun avec celle-ci, et il trouve sensiblement moins
de dépense en 2070 que le dépôt. La piste identifiée est le **taux de
remplacement**, qui ne recule pas dans le modèle alors que le COR le fait
reculer nettement : un modèle dont le taux de remplacement ne recule pas dépense
mécaniquement plus, à démographie identique. Si c'est la bonne piste, la base de
dépense du système actuel est trop haute à l'horizon, ce qui **flatte
l'économie affichée par la proposition** dans les années lointaines. Ce n'est
pas vérifié : il faudrait confronter les deux séries de pension moyenne, série
contre série, ce que le dépôt n'a pas fait. `docs/limites.md`, section « La
trajectoire projetée », tient le détail de cet écart et de son histoire.

### 5. Ni comportement, ni emploi, ni retour de croissance

Le taux de couverture et le taux d'emploi sont supposés constants : le modèle
compte des générations, non des cotisants, et suppose que la même proportion de
chacune perçoit une pension et que la carrière type ne change pas. Aucun effet
de comportement n'est modélisé — ni sur l'âge de départ, ni sur l'offre de
travail que des prélèvements plus faibles libéreraient, ni sur l'épargne. Le
PIB projeté est **unique pour les six systèmes**, ce qui rend les courbes
comparables et suppose du même coup qu'aucune réforme ne déplace son propre
dénominateur. C'est une omission qui joue dans les deux sens, et la seule
défense du chiffrage est qu'elle est symétrique.

### 6. La grille : treize carrières, plafonnées à 2,5 fois le salaire moyen

Tout l'agrégat repose sur le rapport de deux masses calculées sur treize cas
types. Quatre conséquences à connaître :

- **Toute règle qui ne mord qu'au-dessus de 2,5 fois le salaire moyen est
  invisible dans l'agrégat**, en recette comme en dépense. Le déplafonnement de
  l'assiette décidé en septembre 2026 a laissé coût, solde et coefficients
  d'équilibre identiques au centime, faute que personne dans la grille gagne
  assez pour être concerné. La recette qu'un vrai déplafonnement apporterait
  n'est donc pas dans ces tableaux, et la dépense non plus.
- **Un effectif de caisse n'est pas un effectif de personnes** : un
  polypensionné compte dans chacune des siennes, et la somme des caisses dépasse
  la ligne « tous régimes ». Le poids des régimes dont les affiliés ont
  typiquement aussi une carrière au régime général en est gonflé.
- **La Cnav est partagée également entre les quatre carrières du privé**, faute
  qu'aucune source ne dise combien de ses retraités ont été cadres.
- Les cas types comparables s'écartent de l'âge de départ réel de leur catégorie
  socioprofessionnelle, et ces écarts se compensent plutôt qu'ils ne s'annulent.
  Le contrefactuel de `scripts/cout_age_depart.py` dit que cette erreur ne
  déplace pas le résultat agrégé, mais elle est là.

### 7. La garantie repose sur une distribution de 2020 déplacée, et sur un taux de recours conventionnel

Le barème est appliqué à la distribution des pensions de l'échantillon
interrégimes de retraités de la DREES, fin 2020. La **forme** de cette
distribution est supposée inchangée sur toute la série, seulement déplacée, et
le déplacement est proportionnel et uniforme alors que la proposition ne déplace
pas toutes les carrières du même rapport. Le **taux de recours** est fixé à un
ayant droit sur deux, ce que la DREES mesure sur l'ASPA : c'est un réglage, pas
une mesure, et il commande directement le coût. Les retraités de moins de
65 ans, qui attendent la garantie, sont supposés répartis comme les autres. Les
**reprises sur succession** rattachent une pension au patrimoine de son quart
par son rang, faute que le patrimoine des retraités selon leur pension soit
publié nulle part.

### 8. Ce que la garantie remplace est une borne basse

La garantie succède à l'ASPA, au minimum contributif, au minimum garanti de la
fonction publique et à la pension majorée de référence. Le total de ces quatre
minima, que `docs/limites.md` chiffre, est lui-même une **borne basse** : deux
des quatre postes sont calculés sur la grille, qui n'est pas une population et
les sous-estime, et le quatrième n'est pas chiffré du tout. Le surcoût net pour
l'impôt — la garantie moins ce qu'elle remplace — est donc une borne haute.

**Et deux paragraphes de `docs/limites.md` portent encore les chiffres de
garantie d'avant la pondération du recensement.** Ils sont en zone `recit`,
vrais à leur date et gelés, ce qui est le régime voulu ; le contrôle de
fraîcheur passe donc, et c'est normal. Cela ne les rend pas citables dans un
document budgétaire : les valeurs à reprendre sont celles des tableaux
ci-dessus, et le tableau des trois conventions de la même section.

### 9. La suppression de la réversion n'est pas dans le programme écrit

Aucun scénario notionnel ne sert de pension de réversion : c'est le chemin de
la Suède, où un compte notionnel ne verse qu'à son titulaire, et c'est une
décision du dépôt de septembre 2026 plutôt qu'une phrase du programme. Elle est
**déduite** de la règle « aucun avantage non contributif », que la réversion
respecte mal : l'inventaire du dépôt la range parmi eux depuis toujours, et
elle est de très loin la première dépense non contributive du système. Cette
seule décision améliore le solde moyen de la proposition d'un peu plus d'un
point de PIB sur la projection, selon `docs/limites.md` : sans elle, la
variante rétroactive ferait nettement moins bien que le droit en vigueur, au
lieu de faire à peu près aussi mal. La convention italienne — le capital
du défunt se partage — reste calculable par `convention_reversion="servie"`.
C'est probablement la décision politiquement la plus lourde du dossier, et elle
mérite d'être écrite plutôt que déduite.

### 10. Le pilier capitalisé ne porte aucun aléa de marché

Les versements obligatoires du tableau E sont placés sur des titres sans risque
aux taux à terme de la courbe, servis en rente viagère selon la table de
mortalité du modèle, sous les frais du marché de 2025. Aucune variance de
rendement n'est modélisée : la rente affichée est une espérance servie comme
une certitude. `docs/limites.md`, section « Le pilier capitalisé : ce que sa
rente suppose », tient les réserves une à une.

### 11. Ce qui reste ouvert au registre de veille

`data/reference/legislation/veille.yaml` porte encore un **manque** — la table
de durée requise propre aux IEG — et un **à vérifier** : que les articles
`L. 161-17-2` et `L. 161-17-3` n'aient pas de version postérieure au 31 décembre
2025, à contrôler à chaque session par `python scripts/veille_droit.py`.

### 12. La TVA à taux unique est chiffrée en statique

*Ajoutée le 23 septembre 2026, et placée en dernier pour ne pas renuméroter
les autres, que le document cite par leur numéro.* Par son enjeu, elle serait
la première : 2,17 points de PIB, plus qu'aucune autre.

Les assiettes sont celles du modèle de la TVA théorique de la DG Trésor
(Trésor-Éco n° 371, septembre 2025), qui publie ce que rapporterait en 2025 un
point de plus sur chaque taux ; le dépôt en retient le rendement **net**, qui
retire la TVA que les administrations paient sur leurs propres achats. Le taux
moyen des quatre taux sur cette assiette est de 15,46 %, et chaque point de
taux unique au-delà rapporte 0,38 point de PIB. `src/retraite_notionnelle/donnees/tva.py`
tient le calcul. Ce qu'il ne compte pas :

- **aucun effet de volume** : le Trésor le dit de ses propres chiffres, « hors
  effets induits sur les comportements de consommation » ;
- **une répercussion intégrale et symétrique** dans les prix, alors que les
  baisses de TVA passent moins dans les prix que les hausses ;
- **aucun effet de prix sur les dépenses indexées** : à 19,7 %, l'alimentation
  prend 13,5 %, les médicaments remboursables 17,2 %, et toute pension ou
  prestation qui suit l'indice des prix suivrait ;
- **une assiette tenue à sa part de PIB de 2025**, 38,4 %, comme la
  consommation qui la fait ;
- **les arrondis du Trésor**, au dixième de milliard par taux, qui laissent le
  taux moyen entre 15,3 et 15,6 %.

La directive européenne sur la TVA le permet : elle exige un taux normal d'au
moins 15 % et laisse les taux réduits facultatifs.

Et une borne qui vaut pour tout le document : **le contrefactuel ne peut jamais
valoir mieux qu'« estimé ».** La dépense observée est certifiée, recontrôlée
contre l'API de son producteur ; le rapport de masses qui la corrige ne l'est
pas et ne peut pas l'être, aucune institution ne publiant ce qu'un système qui
n'a pas existé aurait coûté.

## Reproduire ces chiffres

```bash
pip install -e '.[dev]'
python scripts/chiffrage_plf.py             # réécrit ce document et la série
python scripts/chiffrage_plf.py --verifier  # échoue s'ils sont périmés
python scripts/proposition_prospective.py   # les deux variantes, années clés
python -m pytest tests/test_cout.py         # ce qui tient les agrégats
```
