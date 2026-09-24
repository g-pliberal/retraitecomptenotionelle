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

*Ajouté le 23 septembre 2026, retiré le 24.* Une **TVA à taux unique**
affectée à la retraite a fait partie de la proposition pendant un jour : les
quatre taux d'aujourd'hui cédaient la place à un seul — 21,1 %, puis 19,7 %,
puis 20 % —, et ce qu'il rapportait de plus allait à la garantie vieillesse,
puis au régime. Le Parti libéral y a renoncé : **la proposition garde les
quatre taux de TVA d'aujourd'hui, et rien de la TVA ne va aux retraites.** Les
tableaux n'en portent plus ; le mécanisme reste dans le modèle, comme
variante (`taux_tva_liberal`).

*Ajouté le même jour, le soir.* Et un **âge légal de départ de 65 ans** à
compter de la bascule : toute pension que la proposition liquide l'est à cet
âge au plus tôt, et qui serait parti avant travaille et cotise jusque-là. Il
fait cotiser davantage et servir moins de pensions : le solde moyen 2026-2070
de la variante rétroactive passe de -1,39 à -0,87 point de PIB. C'est un
plafond : il suppose, comme la page Coût par défaut, que ceux que le report
fait attendre sont en emploi (`part_reportes_en_emploi`) ; si la moitié
seulement l'étaient, ce solde serait de -1,04 point.

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
- **TVA** (*ajouté le 23 septembre 2026, sans objet depuis le 24*) : ce que
  rapportait de plus la TVA à taux unique, quand la proposition la portait.
  Elle payait d'abord la garantie nette et entrait au régime pour le reste, si
  bien que « Solde régime » et « Solde + garantie » étaient égaux dans les
  tableaux A à D. Sans elle, le second retranche de nouveau toute la garantie.
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
| Dépense publique retirée (pensions et garantie) | -4,89 | -150 |
| **Écart de solde de la retraite, garantie comprise, variante rétroactive** | **-0,91** | **-28** |
| **Écart de solde de la retraite, garantie comprise, variante prospective** | **-4,06** | **-125** |
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
20 % la laisse en déficit jusqu'en 2061.

*Corrigé le 24 septembre 2026, la TVA retirée.* Le fait central retrouve son
signe : -0,91 point de PIB en 2026 dans la variante rétroactive, -4,06 dans la
prospective. L'âge légal de 65 ans, venu entre-temps, en rend une part : sans
lui, la variante rétroactive était à -1,44.

## Les quatre arbitrages qui déplacent le chiffrage

Aucun de ces quatre points n'est tranché par le programme écrit. Deux d'entre
eux — les impôts affectés et la rétroactivité — valent chacun, à eux seuls,
plus que l'écart de solde que le tableau précédent affiche.

*Ajouté le 23 septembre 2026.* Une cinquième ligne dit ce que vaut la TVA à
taux unique, décidée ce jour-là : y renoncer ramène la variante rétroactive à
l'écart d'avant elle. Et le coefficient d'équilibre, calculé avec elle, dépasse
un : il ne dit plus de combien il faudrait rogner les pensions, mais de combien
l'excédent permettrait de les relever — ce que personne ne propose.
*Retirée le 24 septembre 2026, avec la TVA.* La ligne a disparu du tableau,
et le coefficient d'équilibre repasse sous un : il dit de nouveau de combien
il faudrait rogner les pensions.

<!-- arbitrages:debut -->
| Arbitrage ouvert | Ce qu'il déplace en 2026 | En milliards |
|---|---:|---:|
| Impôts et taxes affectés, si l'État continue de les lever | +2,14 pt | +66 |
| Subventions d'équilibre, même question | +0,25 pt | +8 |
| Renoncer à la rétroactivité (variante prospective) | -3,15 pt | -97 |
| Appliquer le coefficient d'équilibre, non appliqué ici | 0,93 sur toutes les pensions | soit 7,2 % de moins |
<!-- arbitrages:fin -->

## Tableaux annuels

### A. Variante rétroactive — trajectoire annuelle

<!-- annuel_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 8,80 (270) | 0,44 (14) | 9,24 (283) | 8,17 (250) | -0,63 (-19) | -1,07 (-33) | -0,16 (-5) | -0,91 |
| 2027 | 8,76 (275) | 0,43 (14) | 9,19 (289) | 8,35 (263) | -0,41 (-13) | -0,84 (-26) | -0,22 (-7) | -0,62 |
| 2028 | 8,69 (281) | 0,42 (13) | 9,10 (294) | 8,48 (274) | -0,21 (-7) | -0,63 (-20) | -0,24 (-8) | -0,39 |
| 2029 | 8,62 (287) | 0,40 (13) | 9,02 (300) | 8,50 (283) | -0,11 (-4) | -0,51 (-17) | -0,17 (-6) | -0,34 |
| 2030 | 8,77 (301) | 0,39 (13) | 9,15 (314) | 8,50 (291) | -0,27 (-9) | -0,65 (-22) | -0,20 (-7) | -0,45 |
| 2031 | 8,97 (317) | 0,37 (13) | 9,34 (330) | 8,38 (296) | -0,59 (-21) | -0,96 (-34) | -0,24 (-9) | -0,72 |
| 2032 | 9,04 (329) | 0,36 (13) | 9,40 (342) | 8,42 (306) | -0,62 (-23) | -0,98 (-36) | -0,26 (-10) | -0,72 |
| 2033 | 9,05 (339) | 0,34 (13) | 9,40 (352) | 8,44 (316) | -0,61 (-23) | -0,96 (-36) | -0,27 (-10) | -0,68 |
| 2034 | 9,18 (353) | 0,33 (13) | 9,51 (366) | 8,42 (324) | -0,76 (-29) | -1,09 (-42) | -0,34 (-13) | -0,75 |
| 2035 | 9,26 (366) | 0,31 (12) | 9,58 (379) | 8,43 (333) | -0,84 (-33) | -1,15 (-45) | -0,38 (-15) | -0,77 |
| 2036 | 9,35 (379) | 0,30 (12) | 9,65 (392) | 8,43 (342) | -0,92 (-37) | -1,22 (-49) | -0,43 (-17) | -0,79 |
| 2037 | 9,44 (393) | 0,29 (12) | 9,72 (405) | 8,45 (352) | -0,99 (-41) | -1,27 (-53) | -0,49 (-20) | -0,79 |
| 2038 | 9,52 (407) | 0,27 (12) | 9,79 (418) | 8,43 (360) | -1,08 (-46) | -1,35 (-58) | -0,53 (-23) | -0,82 |
| 2039 | 9,59 (421) | 0,26 (11) | 9,85 (432) | 8,41 (369) | -1,18 (-52) | -1,44 (-63) | -0,57 (-25) | -0,86 |
| 2040 | 9,65 (434) | 0,25 (11) | 9,90 (445) | 8,41 (378) | -1,24 (-56) | -1,49 (-67) | -0,61 (-27) | -0,88 |
<!-- annuel_retroactif:fin -->

### B. Variante rétroactive — horizon long

<!-- horizon_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 9,83 (498) | 0,19 (10) | 10,03 (507) | 8,44 (427) | -1,39 (-70) | -1,59 (-80) | -0,89 (-45) | -0,70 |
| 2050 | 9,87 (555) | 0,16 (9) | 10,03 (564) | 8,43 (474) | -1,44 (-81) | -1,60 (-90) | -1,22 (-68) | -0,38 |
| 2055 | 9,69 (603) | 0,14 (9) | 9,83 (612) | 8,42 (524) | -1,27 (-79) | -1,41 (-88) | -1,54 (-96) | +0,13 |
| 2060 | 9,27 (638) | 0,14 (9) | 9,41 (648) | 8,41 (579) | -0,86 (-59) | -1,00 (-69) | -1,77 (-122) | +0,77 |
| 2065 | 8,79 (667) | 0,14 (10) | 8,92 (677) | 8,42 (639) | -0,37 (-28) | -0,51 (-38) | -2,11 (-160) | +1,60 |
| 2070 | 8,24 (688) | 0,14 (12) | 8,38 (700) | 8,51 (711) | +0,27 (+23) | +0,14 (+11) | -2,39 (-200) | +2,53 |
<!-- horizon_retroactif:fin -->

### C. Variante prospective — trajectoire annuelle

<!-- annuel_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 12,16 (373) | 0,24 (7) | 12,39 (380) | 8,17 (250) | -3,99 (-122) | -4,22 (-129) | -0,16 (-5) | -4,06 |
| 2027 | 12,07 (380) | 0,24 (7) | 12,31 (387) | 8,35 (263) | -3,72 (-117) | -3,96 (-124) | -0,22 (-7) | -3,73 |
| 2028 | 11,88 (384) | 0,23 (8) | 12,11 (392) | 8,48 (274) | -3,40 (-110) | -3,63 (-118) | -0,24 (-8) | -3,40 |
| 2029 | 11,69 (389) | 0,23 (8) | 11,92 (397) | 8,50 (283) | -3,19 (-106) | -3,42 (-114) | -0,17 (-6) | -3,25 |
| 2030 | 11,80 (404) | 0,23 (8) | 12,02 (412) | 8,50 (291) | -3,30 (-113) | -3,52 (-121) | -0,20 (-7) | -3,32 |
| 2031 | 11,98 (423) | 0,22 (8) | 12,20 (431) | 8,38 (296) | -3,60 (-127) | -3,82 (-135) | -0,24 (-9) | -3,58 |
| 2032 | 11,98 (436) | 0,22 (8) | 12,20 (444) | 8,42 (306) | -3,56 (-129) | -3,78 (-138) | -0,26 (-10) | -3,52 |
| 2033 | 11,91 (446) | 0,22 (8) | 12,13 (454) | 8,44 (316) | -3,47 (-130) | -3,69 (-138) | -0,27 (-10) | -3,42 |
| 2034 | 11,98 (461) | 0,21 (8) | 12,19 (469) | 8,42 (324) | -3,56 (-137) | -3,77 (-145) | -0,34 (-13) | -3,43 |
| 2035 | 11,99 (474) | 0,21 (8) | 12,19 (482) | 8,43 (333) | -3,56 (-141) | -3,77 (-149) | -0,38 (-15) | -3,38 |
| 2036 | 12,00 (487) | 0,20 (8) | 12,21 (495) | 8,43 (342) | -3,58 (-145) | -3,78 (-153) | -0,43 (-17) | -3,35 |
| 2037 | 12,03 (501) | 0,20 (8) | 12,23 (509) | 8,45 (352) | -3,58 (-149) | -3,78 (-157) | -0,49 (-20) | -3,29 |
| 2038 | 12,04 (515) | 0,19 (8) | 12,23 (523) | 8,43 (360) | -3,61 (-154) | -3,80 (-162) | -0,53 (-23) | -3,27 |
| 2039 | 12,05 (528) | 0,18 (8) | 12,23 (537) | 8,41 (369) | -3,63 (-159) | -3,81 (-167) | -0,57 (-25) | -3,24 |
| 2040 | 12,03 (541) | 0,18 (8) | 12,21 (549) | 8,41 (378) | -3,62 (-163) | -3,80 (-171) | -0,61 (-27) | -3,19 |
<!-- annuel_prospectif:fin -->

### D. Variante prospective — horizon long

<!-- horizon_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 11,88 (601) | 0,15 (8) | 12,03 (609) | 8,44 (427) | -3,44 (-174) | -3,59 (-181) | -0,89 (-45) | -2,70 |
| 2050 | 11,56 (650) | 0,13 (7) | 11,70 (657) | 8,43 (474) | -3,13 (-176) | -3,26 (-184) | -1,22 (-68) | -2,05 |
| 2055 | 11,05 (688) | 0,12 (8) | 11,17 (695) | 8,42 (524) | -2,63 (-164) | -2,75 (-171) | -1,54 (-96) | -1,21 |
| 2060 | 10,31 (710) | 0,12 (8) | 10,43 (718) | 8,41 (579) | -1,90 (-131) | -2,02 (-139) | -1,77 (-122) | -0,25 |
| 2065 | 9,55 (725) | 0,12 (9) | 9,68 (735) | 8,42 (639) | -1,13 (-86) | -1,26 (-96) | -2,11 (-160) | +0,85 |
| 2070 | 8,76 (732) | 0,13 (11) | 8,89 (743) | 8,51 (711) | -0,25 (-21) | -0,38 (-32) | -2,39 (-200) | +2,01 |
<!-- horizon_prospectif:fin -->

### E. Prélèvements retraite, avant et après, et ce que l'État verse à part

<!-- prelevements:debut -->
| Année | Cotisations (sc. 1) | Impôts et taxes affectés (sc. 1) | **Prélèvements sc. 1** | Cotisations 18 % (sc. 6) | Pilier obligatoire 5 % (sc. 6) | **Prélèvements sc. 6** | Écart | Versé par l'État au sc. 1, hors prélèvements |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 9,16 (281) | 2,14 (66) | **11,30 (346)** | 7,76 (238) | 2,16 (66) | **9,92 (304)** | -1,38 | 1,88 (58) |
| 2030 | 9,10 (312) | 2,13 (73) | **11,23 (385)** | 8,10 (278) | 2,25 (77) | **10,35 (355)** | -0,88 | 1,87 (64) |
| 2035 | 8,93 (353) | 2,08 (82) | **11,01 (435)** | 8,04 (318) | 2,23 (88) | **10,27 (406)** | -0,74 | 1,84 (73) |
| 2040 | 8,81 (397) | 2,06 (93) | **10,87 (489)** | 8,02 (361) | 2,23 (100) | **10,25 (461)** | -0,63 | 1,81 (82) |
| 2050 | 8,63 (485) | 2,01 (113) | **10,64 (598)** | 8,05 (453) | 2,24 (126) | **10,29 (578)** | -0,35 | 1,77 (100) |
| 2060 | 8,51 (586) | 1,99 (137) | **10,50 (722)** | 8,04 (553) | 2,23 (154) | **10,27 (707)** | -0,23 | 1,75 (120) |
| 2070 | 8,47 (708) | 1,98 (165) | **10,45 (873)** | 8,14 (680) | 2,26 (189) | **10,40 (869)** | -0,05 | 1,74 (146) |
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
| Solde moyen, points de PIB | -0,87 | -2,73 | -1,13 |
| Dette accumulée en 2070, points de PIB | +59 | +194 | +66 |
| Première année d'équilibre | 2069 | jamais | jamais |
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

*Corrigé le 24 septembre 2026, la TVA fixée à 20 %.* La variante rétroactive
est en excédent chaque année, au plus juste en 2048, où il lui reste 0,12
point de PIB, et elle aborde 2070 avec des réserves de 41 % du PIB. La
variante prospective reste en déficit de 2026 à 2061, et sa dette atteint 89 %
du PIB en 2070.

*Corrigé le 24 septembre 2026, la TVA retirée.* La variante rétroactive est en
déficit chaque année jusqu'en 2068, au plus bas en 2048, et accumule d'ici 2070
une dette de 59 % du PIB, contre 66 % pour le système actuel : l'âge légal de
65 ans la fait passer sous lui. La variante prospective ne revient jamais à
l'équilibre, et sa dette atteint 194 % du PIB.

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
*Sans objet depuis le 24 septembre 2026* : la proposition ne réforme plus la
TVA, et la question se pose de nouveau entière.

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
*Sans objet depuis le 24 septembre 2026* : sans TVA, le pilotage revient au
coefficient d'équilibre, que le chiffrage n'applique pas.

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
*Ajoutée le 23 septembre 2026, et placée en dernier pour ne pas renuméroter
les autres, que le document cite par leur numéro.* Par son enjeu, elle serait
la première : 2,17 points de PIB, plus qu'aucune autre. *Sans objet depuis le
24 septembre 2026, où la proposition a renoncé à la TVA à taux unique ; elle
reste pour la variante qui la porterait.*

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
- **aucun effet de prix sur les dépenses indexées** : à 20 %, l'alimentation
  prend 13,7 %, les médicaments remboursables 17,5 %, et toute pension ou
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
