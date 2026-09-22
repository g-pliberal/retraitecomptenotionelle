# Chiffrage budgétaire de la proposition, pour un projet de loi de finances

**Tous les tableaux de ce document sont écrits par
`python scripts/chiffrage_plf.py`, qui les recalcule depuis le modèle.** Ne pas
les modifier à la main : `tests/test_prose.py` refuse un document qui ne serait
plus celui que le script produit. La prose, elle, est datée du
22 septembre 2026 et relève du régime `recit` de `docs/fraicheur.md` : elle
raconte ce que ces chiffres voulaient dire ce jour-là.

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

**Deux variantes sont chiffrées, et l'écart entre elles est le premier fait
budgétaire du dossier.**

- **Rétroactive** — la convention par défaut du dépôt, celle que le site
  affiche : toutes les pensions, y compris celles déjà liquidées, sont
  recalculées en comptes notionnels depuis 1941.
- **Prospective** — les droits acquis sont figés à la bascule, débarrassés des
  avantages non contributifs et convertis en capital ; les pensions déjà
  liquidées ne bougent pas. C'est la variante juridiquement soutenable, et
  `scripts/proposition_prospective.py` dit pourquoi.

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
- **Solde + garantie** : le précédent, diminué de la garantie que le
  contribuable porte. **Ce n'est pas un solde toutes administrations
  publiques**, et l'hypothèse n° 1 dit exactement pourquoi.
- **Rappel sc. 1** : le solde du système actuel, même année, même périmètre — le
  compte du COR, qui consolide dépenses et ressources de l'ensemble des régimes
  légalement obligatoires, fonds de solidarité vieillesse compris.
- **Écart** : « Solde + garantie » moins « Rappel sc. 1 ». Négatif, la
  proposition dégrade le solde public par rapport au droit en vigueur.
- La pondération est celle du dépôt : chaque cas type porte l'effectif de
  retraités de sa caisse dans les masses de pensions, et ses cotisants dans les
  masses de cotisations.

## Le fait central

<!-- fait_central:debut -->
| En 2026 | Points de PIB | Milliards d'euros |
|---|---:|---:|
| Recettes retirées au système de retraite | -6,09 | -187 |
| Dépense publique retirée (pensions et garantie) | -4,75 | -146 |
| **Écart de solde public, variante rétroactive** | **-1,34** | **-41** |
| **Écart de solde public, variante prospective** | **-4,95** | **-152** |
<!-- fait_central:fin -->

La proposition retire à la fois des recettes et de la dépense, et **elle en
retire plus du côté des recettes**. C'est le résultat que tout le reste du
document décline : une dépense de pensions qui baisse de plus d'un tiers ne suffit pas
à compenser des prélèvements qui baissent davantage.

## Les quatre arbitrages qui déplacent le chiffrage

Aucun de ces quatre points n'est tranché par le programme écrit. Deux d'entre
eux — les impôts affectés et la rétroactivité — valent chacun, à eux seuls,
plus que l'écart de solde que le tableau précédent affiche.

<!-- arbitrages:debut -->
| Arbitrage ouvert | Ce qu'il déplace en 2026 | En milliards |
|---|---:|---:|
| Impôts et taxes affectés, si l'État continue de les lever | +2,14 pt | +66 |
| Subventions d'équilibre, même question | +0,25 pt | +8 |
| Renoncer à la rétroactivité (variante prospective) | -3,60 pt | -110 |
| Appliquer le coefficient d'équilibre, non appliqué ici | 0,89 sur toutes les pensions | soit 10,6 % de moins |
<!-- arbitrages:fin -->

## Tableaux annuels

### A. Variante rétroactive — trajectoire annuelle

<!-- annuel_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 8,81 (270) | 0,57 (17) | 9,38 (287) | 7,87 (241) | -0,93 (-29) | -1,51 (-46) | -0,16 (-5) | -1,34 |
| 2027 | 8,91 (280) | 0,56 (17) | 9,47 (298) | 7,85 (247) | -1,06 (-33) | -1,61 (-51) | -0,22 (-7) | -1,39 |
| 2028 | 8,97 (290) | 0,53 (17) | 9,50 (307) | 7,84 (253) | -1,13 (-36) | -1,66 (-54) | -0,24 (-8) | -1,42 |
| 2029 | 8,93 (297) | 0,51 (17) | 9,44 (314) | 7,83 (261) | -1,10 (-37) | -1,61 (-54) | -0,17 (-6) | -1,44 |
| 2030 | 8,98 (308) | 0,49 (17) | 9,47 (325) | 7,83 (268) | -1,14 (-39) | -1,64 (-56) | -0,20 (-7) | -1,44 |
| 2031 | 9,02 (319) | 0,47 (17) | 9,49 (335) | 7,83 (277) | -1,19 (-42) | -1,66 (-59) | -0,24 (-9) | -1,42 |
| 2032 | 9,02 (328) | 0,46 (17) | 9,48 (345) | 7,83 (285) | -1,19 (-43) | -1,65 (-60) | -0,26 (-10) | -1,38 |
| 2033 | 9,05 (339) | 0,44 (16) | 9,49 (355) | 7,83 (293) | -1,22 (-46) | -1,66 (-62) | -0,27 (-10) | -1,39 |
| 2034 | 9,12 (351) | 0,42 (16) | 9,54 (367) | 7,83 (301) | -1,29 (-50) | -1,71 (-66) | -0,34 (-13) | -1,37 |
| 2035 | 9,17 (363) | 0,40 (16) | 9,58 (379) | 7,83 (309) | -1,34 (-53) | -1,75 (-69) | -0,38 (-15) | -1,37 |
| 2036 | 9,23 (375) | 0,39 (16) | 9,62 (390) | 7,83 (318) | -1,40 (-57) | -1,79 (-73) | -0,43 (-17) | -1,36 |
| 2037 | 9,28 (387) | 0,38 (16) | 9,66 (402) | 7,83 (326) | -1,46 (-61) | -1,83 (-76) | -0,49 (-20) | -1,35 |
| 2038 | 9,32 (399) | 0,36 (15) | 9,69 (414) | 7,83 (334) | -1,50 (-64) | -1,86 (-80) | -0,53 (-23) | -1,33 |
| 2039 | 9,36 (411) | 0,35 (15) | 9,71 (426) | 7,83 (343) | -1,54 (-67) | -1,89 (-83) | -0,57 (-25) | -1,31 |
| 2040 | 9,39 (423) | 0,33 (15) | 9,72 (438) | 7,82 (352) | -1,57 (-70) | -1,90 (-86) | -0,61 (-27) | -1,29 |
<!-- annuel_retroactif:fin -->

### B. Variante rétroactive — horizon long

<!-- horizon_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 9,51 (481) | 0,27 (14) | 9,79 (495) | 7,82 (396) | -1,69 (-86) | -1,97 (-99) | -0,89 (-45) | -1,08 |
| 2050 | 9,47 (532) | 0,24 (13) | 9,70 (546) | 7,82 (440) | -1,65 (-93) | -1,88 (-106) | -1,22 (-68) | -0,67 |
| 2055 | 9,25 (576) | 0,21 (13) | 9,47 (589) | 7,82 (487) | -1,43 (-89) | -1,65 (-103) | -1,54 (-96) | -0,11 |
| 2060 | 8,85 (609) | 0,20 (14) | 9,05 (623) | 7,82 (538) | -1,03 (-71) | -1,23 (-85) | -1,77 (-122) | +0,54 |
| 2065 | 8,42 (640) | 0,19 (15) | 8,62 (654) | 7,82 (593) | -0,61 (-46) | -0,80 (-61) | -2,11 (-160) | +1,31 |
| 2070 | 7,94 (663) | 0,19 (16) | 8,13 (679) | 7,81 (653) | -0,12 (-10) | -0,31 (-26) | -2,39 (-200) | +2,08 |
<!-- horizon_retroactif:fin -->

### C. Variante prospective — trajectoire annuelle

<!-- annuel_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 12,66 (388) | 0,32 (10) | 12,98 (398) | 7,87 (241) | -4,79 (-147) | -5,11 (-157) | -0,16 (-5) | -4,95 |
| 2027 | 12,74 (401) | 0,32 (10) | 13,06 (411) | 7,85 (247) | -4,89 (-154) | -5,21 (-164) | -0,22 (-7) | -4,98 |
| 2028 | 12,74 (412) | 0,31 (10) | 13,06 (422) | 7,84 (253) | -4,90 (-159) | -5,22 (-169) | -0,24 (-8) | -4,98 |
| 2029 | 12,62 (420) | 0,31 (10) | 12,92 (430) | 7,83 (261) | -4,78 (-159) | -5,09 (-169) | -0,17 (-6) | -4,92 |
| 2030 | 12,60 (432) | 0,30 (10) | 12,91 (442) | 7,83 (268) | -4,77 (-164) | -5,07 (-174) | -0,20 (-7) | -4,87 |
| 2031 | 12,59 (445) | 0,30 (10) | 12,88 (455) | 7,83 (277) | -4,76 (-168) | -5,05 (-178) | -0,24 (-9) | -4,81 |
| 2032 | 12,55 (457) | 0,29 (11) | 12,84 (467) | 7,83 (285) | -4,72 (-172) | -5,01 (-182) | -0,26 (-10) | -4,75 |
| 2033 | 12,52 (469) | 0,28 (11) | 12,80 (479) | 7,83 (293) | -4,69 (-176) | -4,97 (-186) | -0,27 (-10) | -4,70 |
| 2034 | 12,53 (482) | 0,27 (11) | 12,80 (493) | 7,83 (301) | -4,70 (-181) | -4,98 (-191) | -0,34 (-13) | -4,64 |
| 2035 | 12,52 (495) | 0,27 (11) | 12,79 (506) | 7,83 (309) | -4,69 (-186) | -4,96 (-196) | -0,38 (-15) | -4,58 |
| 2036 | 12,52 (508) | 0,26 (11) | 12,78 (519) | 7,83 (318) | -4,69 (-190) | -4,96 (-201) | -0,43 (-17) | -4,53 |
| 2037 | 12,51 (521) | 0,26 (11) | 12,77 (532) | 7,83 (326) | -4,68 (-195) | -4,94 (-206) | -0,49 (-20) | -4,45 |
| 2038 | 12,49 (534) | 0,25 (11) | 12,74 (545) | 7,83 (334) | -4,66 (-199) | -4,91 (-210) | -0,53 (-23) | -4,38 |
| 2039 | 12,46 (547) | 0,25 (11) | 12,71 (557) | 7,83 (343) | -4,63 (-203) | -4,88 (-214) | -0,57 (-25) | -4,31 |
| 2040 | 12,42 (559) | 0,24 (11) | 12,66 (570) | 7,82 (352) | -4,59 (-207) | -4,83 (-218) | -0,61 (-27) | -4,22 |
<!-- annuel_prospectif:fin -->

### D. Variante prospective — horizon long

<!-- horizon_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 12,20 (617) | 0,21 (11) | 12,41 (628) | 7,82 (396) | -4,38 (-222) | -4,59 (-232) | -0,89 (-45) | -3,71 |
| 2050 | 11,78 (662) | 0,19 (11) | 11,98 (673) | 7,82 (440) | -3,96 (-223) | -4,16 (-234) | -1,22 (-68) | -2,94 |
| 2055 | 11,18 (696) | 0,18 (11) | 11,36 (707) | 7,82 (487) | -3,36 (-209) | -3,55 (-221) | -1,54 (-96) | -2,01 |
| 2060 | 10,37 (714) | 0,18 (12) | 10,55 (726) | 7,82 (538) | -2,56 (-176) | -2,74 (-188) | -1,77 (-122) | -0,97 |
| 2065 | 9,57 (727) | 0,18 (14) | 9,75 (740) | 7,82 (593) | -1,75 (-133) | -1,93 (-147) | -2,11 (-160) | +0,18 |
| 2070 | 8,73 (729) | 0,18 (15) | 8,91 (744) | 7,81 (653) | -0,92 (-77) | -1,10 (-92) | -2,39 (-200) | +1,29 |
<!-- horizon_prospectif:fin -->

### E. Prélèvements obligatoires retraite, avant et après

<!-- prelevements:debut -->
| Année | Cotisations + contribution d'équilibre (sc. 1) | Impôts et taxes affectés (sc. 1) | Subventions d'équilibre (sc. 1) | **Total sc. 1** | Cotisations 18 % (sc. 6) | Pilier obligatoire 5 % (sc. 6) | **Total sc. 6** | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 10,79 (331) | 2,14 (66) | 0,25 (8) | **13,19 (404)** | 7,60 (233) | 2,11 (65) | **9,72 (298)** | -3,47 |
| 2030 | 10,72 (368) | 2,13 (73) | 0,25 (9) | **13,10 (449)** | 7,57 (259) | 2,10 (72) | **9,67 (331)** | -3,43 |
| 2035 | 10,52 (416) | 2,08 (82) | 0,25 (10) | **12,85 (508)** | 7,57 (299) | 2,10 (83) | **9,67 (382)** | -3,18 |
| 2040 | 10,38 (467) | 2,06 (93) | 0,24 (11) | **12,69 (571)** | 7,57 (341) | 2,10 (95) | **9,67 (435)** | -3,02 |
| 2050 | 10,16 (571) | 2,01 (113) | 0,24 (13) | **12,41 (698)** | 7,57 (425) | 2,10 (118) | **9,67 (544)** | -2,75 |
| 2060 | 10,02 (690) | 1,99 (137) | 0,24 (16) | **12,25 (843)** | 7,57 (521) | 2,10 (145) | **9,67 (666)** | -2,58 |
| 2070 | 9,98 (833) | 1,98 (165) | 0,23 (20) | **12,19 (1 018)** | 7,57 (632) | 2,10 (176) | **9,67 (808)** | -2,52 |
<!-- prelevements:fin -->

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
| Dépense de pensions cumulée, Md € constants de 2026 | 15 816 | 19 834 | 25 380 |
| Écart de dépense au système actuel | -9 564 | -5 546 | — |
| Garantie vieillesse brute cumulée | 713 | 544 | — |
| Reprises sur succession | -239 | -189 | — |
| Garantie nette cumulée | 474 | 355 | — |
| Solde moyen, points de PIB | -1,22 | -3,63 | -1,13 |
| Dette accumulée en 2070, points de PIB | +84 | +256 | +66 |
| Première année d'équilibre | jamais | jamais | jamais |
<!-- agregats:fin -->

La variante rétroactive ne fait pas mieux que le droit en vigueur sur la
moyenne de la projection : elle est meilleure après le milieu du siècle, pire
avant, et le stock de dette qu'elle accumule d'ici 2070 dépasse celui du
système actuel. La variante prospective en accumule plusieurs fois plus.

## La pondération du recensement

Elle n'intervient qu'à un endroit, et elle y vaut un cinquième du coût de la
garantie vieillesse. La garantie sert deux planchers — 800 € par personne,
1 050 € pour qui vit seul — et l'enquête sur les pensions ne dit pas avec qui
l'on vit. Le recensement le dit, lui, âge par âge et par sexe. Pesé sur les
années vécues après 65 ans, et avec la table de mortalité du **premier
vingtile** — celle des bénéficiaires, qui meurent plus tôt et pèsent donc moins
les grands âges, ceux où l'on vit seul —, il donne une proportion de femmes
vivant seules près du double de celle des hommes, et les deux planchers se
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

Rien ne devrait être déposé avant que ce point soit écrit.

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
