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
| Recettes retirées au système de retraite | -5,96 | -183 |
| Dépense publique retirée (pensions et garantie) | -4,40 | -135 |
| **Écart de solde public, variante rétroactive** | **-1,55** | **-48** |
| **Écart de solde public, variante prospective** | **-4,80** | **-147** |
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
| Renoncer à la rétroactivité (variante prospective) | -3,25 pt | -100 |
| Appliquer le coefficient d'équilibre, non appliqué ici | 0,87 sur toutes les pensions | soit 12,8 % de moins |
<!-- arbitrages:fin -->

## Tableaux annuels

### A. Variante rétroactive — trajectoire annuelle

<!-- annuel_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 9,18 (282) | 0,54 (17) | 9,72 (298) | 8,01 (245) | -1,18 (-36) | -1,72 (-53) | -0,16 (-5) | -1,55 |
| 2027 | 9,29 (292) | 0,53 (17) | 9,83 (309) | 7,99 (251) | -1,30 (-41) | -1,83 (-58) | -0,22 (-7) | -1,61 |
| 2028 | 9,36 (303) | 0,51 (17) | 9,87 (319) | 7,98 (258) | -1,38 (-45) | -1,89 (-61) | -0,24 (-8) | -1,65 |
| 2029 | 9,32 (310) | 0,50 (17) | 9,82 (327) | 7,97 (265) | -1,36 (-45) | -1,85 (-62) | -0,17 (-6) | -1,68 |
| 2030 | 9,38 (321) | 0,48 (17) | 9,86 (338) | 7,97 (273) | -1,41 (-48) | -1,89 (-65) | -0,20 (-7) | -1,69 |
| 2031 | 9,43 (333) | 0,47 (17) | 9,89 (349) | 7,96 (281) | -1,46 (-52) | -1,93 (-68) | -0,24 (-9) | -1,69 |
| 2032 | 9,43 (343) | 0,45 (16) | 9,88 (359) | 7,96 (290) | -1,46 (-53) | -1,92 (-70) | -0,26 (-10) | -1,66 |
| 2033 | 9,46 (354) | 0,44 (16) | 9,90 (371) | 7,96 (298) | -1,50 (-56) | -1,94 (-73) | -0,27 (-10) | -1,66 |
| 2034 | 9,53 (367) | 0,42 (16) | 9,95 (383) | 7,96 (306) | -1,57 (-61) | -1,99 (-77) | -0,34 (-13) | -1,65 |
| 2035 | 9,59 (379) | 0,40 (16) | 10,00 (395) | 7,96 (315) | -1,63 (-65) | -2,04 (-81) | -0,38 (-15) | -1,65 |
| 2036 | 9,65 (392) | 0,39 (16) | 10,04 (408) | 7,96 (323) | -1,69 (-69) | -2,08 (-85) | -0,43 (-17) | -1,66 |
| 2037 | 9,71 (404) | 0,37 (16) | 10,09 (420) | 7,96 (331) | -1,75 (-73) | -2,13 (-89) | -0,49 (-20) | -1,64 |
| 2038 | 9,76 (417) | 0,36 (15) | 10,12 (432) | 7,96 (340) | -1,80 (-77) | -2,16 (-92) | -0,53 (-23) | -1,63 |
| 2039 | 9,80 (430) | 0,35 (15) | 10,14 (445) | 7,96 (349) | -1,84 (-81) | -2,18 (-96) | -0,57 (-25) | -1,61 |
| 2040 | 9,82 (442) | 0,33 (15) | 10,15 (457) | 7,96 (358) | -1,87 (-84) | -2,20 (-99) | -0,61 (-27) | -1,59 |
<!-- annuel_retroactif:fin -->

### B. Variante rétroactive — horizon long

<!-- horizon_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 9,93 (503) | 0,27 (14) | 10,20 (516) | 7,95 (402) | -1,98 (-100) | -2,25 (-114) | -0,89 (-45) | -1,36 |
| 2050 | 9,84 (553) | 0,23 (13) | 10,07 (566) | 7,95 (447) | -1,89 (-106) | -2,12 (-119) | -1,22 (-68) | -0,90 |
| 2055 | 9,55 (594) | 0,21 (13) | 9,76 (607) | 7,94 (494) | -1,61 (-100) | -1,81 (-113) | -1,54 (-96) | -0,28 |
| 2060 | 9,06 (623) | 0,20 (14) | 9,26 (637) | 7,94 (547) | -1,11 (-77) | -1,31 (-91) | -1,77 (-122) | +0,45 |
| 2065 | 8,54 (649) | 0,20 (15) | 8,74 (664) | 7,94 (603) | -0,60 (-46) | -0,80 (-61) | -2,11 (-160) | +1,31 |
| 2070 | 7,98 (667) | 0,20 (17) | 8,19 (684) | 7,94 (663) | -0,04 (-4) | -0,25 (-21) | -2,39 (-200) | +2,14 |
<!-- horizon_retroactif:fin -->

### C. Variante prospective — trajectoire annuelle

<!-- annuel_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 12,65 (388) | 0,32 (10) | 12,97 (398) | 8,01 (245) | -4,65 (-142) | -4,96 (-152) | -0,16 (-5) | -4,80 |
| 2027 | 12,74 (400) | 0,32 (10) | 13,05 (410) | 7,99 (251) | -4,74 (-149) | -5,06 (-159) | -0,22 (-7) | -4,84 |
| 2028 | 12,74 (412) | 0,31 (10) | 13,05 (422) | 7,98 (258) | -4,76 (-154) | -5,08 (-164) | -0,24 (-8) | -4,84 |
| 2029 | 12,61 (420) | 0,31 (10) | 12,92 (430) | 7,97 (265) | -4,64 (-154) | -4,95 (-165) | -0,17 (-6) | -4,78 |
| 2030 | 12,60 (432) | 0,31 (11) | 12,91 (442) | 7,97 (273) | -4,63 (-159) | -4,94 (-169) | -0,20 (-7) | -4,74 |
| 2031 | 12,58 (444) | 0,31 (11) | 12,89 (455) | 7,96 (281) | -4,62 (-163) | -4,92 (-174) | -0,24 (-9) | -4,68 |
| 2032 | 12,55 (457) | 0,30 (11) | 12,85 (468) | 7,96 (290) | -4,59 (-167) | -4,89 (-178) | -0,26 (-10) | -4,63 |
| 2033 | 12,52 (469) | 0,30 (11) | 12,81 (480) | 7,96 (298) | -4,56 (-171) | -4,85 (-182) | -0,27 (-10) | -4,58 |
| 2034 | 12,53 (482) | 0,29 (11) | 12,82 (493) | 7,96 (306) | -4,57 (-176) | -4,86 (-187) | -0,34 (-13) | -4,52 |
| 2035 | 12,53 (495) | 0,28 (11) | 12,81 (507) | 7,96 (315) | -4,57 (-181) | -4,85 (-192) | -0,38 (-15) | -4,47 |
| 2036 | 12,53 (509) | 0,28 (11) | 12,81 (520) | 7,96 (323) | -4,58 (-186) | -4,85 (-197) | -0,43 (-17) | -4,42 |
| 2037 | 12,53 (522) | 0,27 (11) | 12,80 (533) | 7,96 (331) | -4,57 (-190) | -4,84 (-202) | -0,49 (-20) | -4,36 |
| 2038 | 12,51 (535) | 0,26 (11) | 12,78 (546) | 7,96 (340) | -4,56 (-195) | -4,82 (-206) | -0,53 (-23) | -4,29 |
| 2039 | 12,49 (548) | 0,26 (11) | 12,75 (559) | 7,96 (349) | -4,53 (-199) | -4,79 (-210) | -0,57 (-25) | -4,22 |
| 2040 | 12,45 (560) | 0,25 (11) | 12,70 (572) | 7,96 (358) | -4,50 (-202) | -4,75 (-214) | -0,61 (-27) | -4,14 |
<!-- annuel_prospectif:fin -->

### D. Variante prospective — horizon long

<!-- horizon_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 12,25 (620) | 0,21 (11) | 12,46 (631) | 7,95 (402) | -4,30 (-217) | -4,51 (-228) | -0,89 (-45) | -3,63 |
| 2050 | 11,82 (664) | 0,19 (11) | 12,01 (675) | 7,95 (447) | -3,87 (-217) | -4,06 (-228) | -1,22 (-68) | -2,84 |
| 2055 | 11,18 (696) | 0,18 (11) | 11,36 (707) | 7,94 (494) | -3,23 (-201) | -3,42 (-213) | -1,54 (-96) | -1,88 |
| 2060 | 10,33 (711) | 0,18 (12) | 10,51 (724) | 7,94 (547) | -2,39 (-165) | -2,57 (-177) | -1,77 (-122) | -0,80 |
| 2065 | 9,49 (721) | 0,19 (14) | 9,68 (735) | 7,94 (603) | -1,55 (-118) | -1,74 (-132) | -2,11 (-160) | +0,37 |
| 2070 | 8,64 (721) | 0,19 (16) | 8,83 (738) | 7,94 (663) | -0,70 (-58) | -0,89 (-74) | -2,39 (-200) | +1,50 |
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
| Dépense de pensions cumulée, Md € constants de 2026 | 16 353 | 19 825 | 25 379 |
| Écart de dépense au système actuel | -9 026 | -5 554 | — |
| Garantie vieillesse brute cumulée | 718 | 568 | — |
| Reprises sur succession | -250 | -206 | — |
| Garantie nette cumulée | 468 | 363 | — |
| Solde moyen, points de PIB | -1,41 | -3,49 | -1,13 |
| Dette accumulée en 2070, points de PIB | +98 | +248 | +66 |
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
