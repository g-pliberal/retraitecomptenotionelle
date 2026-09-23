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
| Recettes retirées au système de retraite | -5,96 | -183 |
| dont cotisations, au taux unique | -1,56 | -48 |
| dont impôts et taxes affectés | -2,14 | -66 |
| dont versements de l'État et de la branche famille | -2,26 | -69 |
| Dépense publique retirée (pensions et garantie) | -4,51 | -138 |
| **Écart de solde de la retraite, garantie comprise, variante rétroactive** | **-1,45** | **-44** |
| **Écart de solde de la retraite, garantie comprise, variante prospective** | **-4,72** | **-145** |
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

## Les quatre arbitrages qui déplacent le chiffrage

Aucun de ces quatre points n'est tranché par le programme écrit. Deux d'entre
eux — les impôts affectés et la rétroactivité — valent chacun, à eux seuls,
plus que l'écart de solde que le tableau précédent affiche.

<!-- arbitrages:debut -->
| Arbitrage ouvert | Ce qu'il déplace en 2026 | En milliards |
|---|---:|---:|
| Impôts et taxes affectés, si l'État continue de les lever | +2,14 pt | +66 |
| Subventions d'équilibre, même question | +0,25 pt | +8 |
| Renoncer à la rétroactivité (variante prospective) | -3,27 pt | -100 |
| Appliquer le coefficient d'équilibre, non appliqué ici | 0,87 sur toutes les pensions | soit 12,7 % de moins |
<!-- arbitrages:fin -->

## Tableaux annuels

### A. Variante rétroactive — trajectoire annuelle

<!-- annuel_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 9,18 (281) | 0,44 (14) | 9,62 (295) | 8,01 (245) | -1,17 (-36) | -1,61 (-49) | -0,16 (-5) | -1,45 |
| 2027 | 9,29 (292) | 0,43 (14) | 9,72 (306) | 7,99 (251) | -1,30 (-41) | -1,73 (-54) | -0,22 (-7) | -1,51 |
| 2028 | 9,35 (302) | 0,42 (13) | 9,77 (316) | 7,98 (258) | -1,38 (-44) | -1,79 (-58) | -0,24 (-8) | -1,55 |
| 2029 | 9,32 (310) | 0,40 (13) | 9,72 (324) | 7,97 (265) | -1,35 (-45) | -1,75 (-58) | -0,17 (-6) | -1,58 |
| 2030 | 9,37 (321) | 0,39 (13) | 9,76 (335) | 7,97 (273) | -1,40 (-48) | -1,79 (-61) | -0,20 (-7) | -1,59 |
| 2031 | 9,42 (333) | 0,38 (13) | 9,80 (346) | 7,96 (281) | -1,46 (-51) | -1,83 (-65) | -0,24 (-9) | -1,59 |
| 2032 | 9,42 (343) | 0,36 (13) | 9,78 (356) | 7,96 (290) | -1,46 (-53) | -1,82 (-66) | -0,26 (-10) | -1,56 |
| 2033 | 9,46 (354) | 0,35 (13) | 9,80 (367) | 7,96 (298) | -1,49 (-56) | -1,84 (-69) | -0,27 (-10) | -1,57 |
| 2034 | 9,53 (367) | 0,33 (13) | 9,86 (379) | 7,96 (306) | -1,57 (-60) | -1,90 (-73) | -0,34 (-13) | -1,56 |
| 2035 | 9,59 (379) | 0,32 (13) | 9,91 (392) | 7,96 (315) | -1,63 (-64) | -1,95 (-77) | -0,38 (-15) | -1,56 |
| 2036 | 9,65 (392) | 0,31 (12) | 9,95 (404) | 7,96 (323) | -1,69 (-69) | -1,99 (-81) | -0,43 (-17) | -1,57 |
| 2037 | 9,70 (404) | 0,29 (12) | 10,00 (416) | 7,96 (331) | -1,75 (-73) | -2,04 (-85) | -0,49 (-20) | -1,55 |
| 2038 | 9,75 (417) | 0,28 (12) | 10,03 (429) | 7,96 (340) | -1,79 (-77) | -2,07 (-89) | -0,53 (-23) | -1,54 |
| 2039 | 9,79 (429) | 0,27 (12) | 10,06 (441) | 7,96 (349) | -1,83 (-80) | -2,10 (-92) | -0,57 (-25) | -1,53 |
| 2040 | 9,82 (442) | 0,26 (12) | 10,07 (453) | 7,96 (358) | -1,86 (-84) | -2,12 (-95) | -0,61 (-27) | -1,51 |
<!-- annuel_retroactif:fin -->

### B. Variante rétroactive — horizon long

<!-- horizon_retroactif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 9,93 (502) | 0,20 (10) | 10,13 (513) | 7,95 (402) | -1,97 (-100) | -2,18 (-110) | -0,89 (-45) | -1,29 |
| 2050 | 9,83 (553) | 0,17 (10) | 10,00 (562) | 7,95 (447) | -1,88 (-106) | -2,06 (-116) | -1,22 (-68) | -0,84 |
| 2055 | 9,54 (594) | 0,15 (10) | 9,70 (604) | 7,94 (494) | -1,60 (-100) | -1,75 (-109) | -1,54 (-96) | -0,21 |
| 2060 | 9,05 (623) | 0,15 (10) | 9,20 (633) | 7,94 (547) | -1,11 (-76) | -1,26 (-87) | -1,77 (-122) | +0,51 |
| 2065 | 8,54 (648) | 0,15 (11) | 8,69 (659) | 7,94 (603) | -0,60 (-45) | -0,74 (-56) | -2,11 (-160) | +1,36 |
| 2070 | 7,98 (667) | 0,15 (13) | 8,13 (679) | 7,94 (663) | -0,04 (-3) | -0,19 (-16) | -2,39 (-200) | +2,20 |
<!-- horizon_retroactif:fin -->

### C. Variante prospective — trajectoire annuelle

<!-- annuel_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 12,65 (388) | 0,24 (7) | 12,89 (395) | 8,01 (245) | -4,64 (-142) | -4,88 (-150) | -0,16 (-5) | -4,72 |
| 2027 | 12,73 (400) | 0,24 (7) | 12,97 (408) | 7,99 (251) | -4,74 (-149) | -4,98 (-157) | -0,22 (-7) | -4,76 |
| 2028 | 12,74 (412) | 0,23 (8) | 12,97 (419) | 7,98 (258) | -4,76 (-154) | -4,99 (-161) | -0,24 (-8) | -4,75 |
| 2029 | 12,61 (420) | 0,23 (8) | 12,84 (427) | 7,97 (265) | -4,64 (-154) | -4,87 (-162) | -0,17 (-6) | -4,70 |
| 2030 | 12,60 (432) | 0,23 (8) | 12,82 (440) | 7,97 (273) | -4,63 (-159) | -4,86 (-166) | -0,20 (-7) | -4,66 |
| 2031 | 12,58 (444) | 0,22 (8) | 12,80 (452) | 7,96 (281) | -4,62 (-163) | -4,84 (-171) | -0,24 (-9) | -4,60 |
| 2032 | 12,55 (457) | 0,22 (8) | 12,77 (465) | 7,96 (290) | -4,59 (-167) | -4,81 (-175) | -0,26 (-10) | -4,55 |
| 2033 | 12,52 (469) | 0,22 (8) | 12,73 (477) | 7,96 (298) | -4,55 (-171) | -4,77 (-179) | -0,27 (-10) | -4,50 |
| 2034 | 12,53 (482) | 0,21 (8) | 12,74 (490) | 7,96 (306) | -4,57 (-176) | -4,78 (-184) | -0,34 (-13) | -4,44 |
| 2035 | 12,53 (495) | 0,21 (8) | 12,73 (503) | 7,96 (315) | -4,57 (-181) | -4,78 (-189) | -0,38 (-15) | -4,39 |
| 2036 | 12,53 (509) | 0,20 (8) | 12,73 (517) | 7,96 (323) | -4,57 (-186) | -4,78 (-194) | -0,43 (-17) | -4,35 |
| 2037 | 12,53 (522) | 0,20 (8) | 12,72 (530) | 7,96 (331) | -4,57 (-190) | -4,77 (-198) | -0,49 (-20) | -4,28 |
| 2038 | 12,51 (535) | 0,19 (8) | 12,70 (543) | 7,96 (340) | -4,55 (-195) | -4,75 (-203) | -0,53 (-23) | -4,22 |
| 2039 | 12,49 (548) | 0,19 (8) | 12,67 (556) | 7,96 (349) | -4,53 (-199) | -4,72 (-207) | -0,57 (-25) | -4,14 |
| 2040 | 12,45 (560) | 0,18 (8) | 12,63 (568) | 7,96 (358) | -4,49 (-202) | -4,67 (-210) | -0,61 (-27) | -4,07 |
<!-- annuel_prospectif:fin -->

### D. Variante prospective — horizon long

<!-- horizon_prospectif:debut -->
| Année | Pensions | Garantie nette | Dépense totale | Recettes | Solde régime | Solde + garantie | Rappel sc. 1 | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2045 | 12,24 (619) | 0,15 (8) | 12,40 (627) | 7,95 (402) | -4,29 (-217) | -4,44 (-225) | -0,89 (-45) | -3,56 |
| 2050 | 11,81 (664) | 0,14 (8) | 11,94 (672) | 7,95 (447) | -3,86 (-217) | -4,00 (-225) | -1,22 (-68) | -2,78 |
| 2055 | 11,17 (695) | 0,13 (8) | 11,30 (703) | 7,94 (494) | -3,23 (-201) | -3,36 (-209) | -1,54 (-96) | -1,82 |
| 2060 | 10,33 (711) | 0,13 (9) | 10,45 (720) | 7,94 (547) | -2,38 (-164) | -2,51 (-173) | -1,77 (-122) | -0,74 |
| 2065 | 9,49 (720) | 0,13 (10) | 9,62 (730) | 7,94 (603) | -1,55 (-117) | -1,68 (-127) | -2,11 (-160) | +0,43 |
| 2070 | 8,63 (721) | 0,14 (12) | 8,77 (733) | 7,94 (663) | -0,69 (-58) | -0,83 (-69) | -2,39 (-200) | +1,56 |
<!-- horizon_prospectif:fin -->

### E. Prélèvements retraite, avant et après, et ce que l'État verse à part

<!-- prelevements:debut -->
| Année | Cotisations (sc. 1) | Impôts et taxes affectés (sc. 1) | **Prélèvements sc. 1** | Cotisations 18 % (sc. 6) | Pilier obligatoire 5 % (sc. 6) | **Prélèvements sc. 6** | Écart | Versé par l'État au sc. 1, hors prélèvements |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 9,16 (281) | 2,14 (66) | **11,30 (346)** | 7,60 (233) | 2,11 (65) | **9,72 (298)** | -1,58 | 1,88 (58) |
| 2030 | 9,10 (312) | 2,13 (73) | **11,23 (385)** | 7,57 (259) | 2,10 (72) | **9,67 (331)** | -1,56 | 1,87 (64) |
| 2035 | 8,93 (353) | 2,08 (82) | **11,01 (435)** | 7,57 (299) | 2,10 (83) | **9,67 (382)** | -1,34 | 1,84 (73) |
| 2040 | 8,81 (397) | 2,06 (93) | **10,87 (489)** | 7,57 (341) | 2,10 (95) | **9,67 (435)** | -1,20 | 1,81 (82) |
| 2050 | 8,63 (485) | 2,01 (113) | **10,64 (598)** | 7,57 (425) | 2,10 (118) | **9,67 (544)** | -0,97 | 1,77 (100) |
| 2060 | 8,51 (586) | 1,99 (137) | **10,50 (722)** | 7,57 (521) | 2,10 (145) | **9,67 (666)** | -0,83 | 1,75 (120) |
| 2070 | 8,47 (708) | 1,98 (165) | **10,45 (873)** | 7,57 (632) | 2,10 (176) | **9,67 (808)** | -0,78 | 1,74 (146) |
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
| Dépense de pensions cumulée, Md € constants de 2026 | 15 155 | 18 450 | 23 442 |
| Écart de dépense au système actuel | -8 287 | -4 992 | — |
| Garantie vieillesse brute cumulée | 561 | 423 | — |
| Reprises sur succession | -201 | -162 | — |
| Garantie nette cumulée | 361 | 261 | — |
| Solde moyen, points de PIB | -1,40 | -3,49 | -1,13 |
| Dette accumulée en 2070, points de PIB | +97 | +247 | +66 |
| Première année d'équilibre | jamais | jamais | jamais |
<!-- agregats:fin -->

La variante rétroactive ne fait pas mieux que le droit en vigueur sur la
moyenne de la projection : elle est meilleure après le milieu du siècle, pire
avant, et le stock de dette qu'elle accumule d'ici 2070 dépasse celui du
système actuel. La variante prospective en accumule plusieurs fois plus.

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

*Ajouté le 23 septembre 2026.* Le solde consolidé est meilleur, en outre, de
ce que l'État employeur et la branche famille cessent de verser à la retraite :
la contribution d'équilibre, qui couvre les pensions des fonctionnaires de
l'État, et l'assurance vieillesse des parents au foyer. Le fait central les
isole, avec les subventions : ce ne sont pas des impôts qu'on lève ou qu'on
abandonne, mais des dépenses que leur payeur ne fait plus. Moins, pour l'État,
sa part d'employeur du taux unique, que le modèle ne sépare pas des autres
cotisations.

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
