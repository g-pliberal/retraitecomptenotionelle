# Les décisions sur les recettes, portées au scénario 6 : le plan, et sa première étape

**Reprise, au 9 novembre 2026.** Le plan est écrit, neuf étapes, une par
session (« Le plan »). Trois sont faites : la part de TVA de l'Agirc-Arrco en
donnée (1), cette TVA au coût du scénario 6 (2) et le point de LVT des
retraites (4), ces deux-là par une autre session le même soir
(`2026-11-09-tva-et-lvt-au-cout.md`). Le propriétaire a répondu aux deux
questions de la fin : la TVA s'ajoute, la LVT à sa valeur centrale
(décisions 105 et 106). Le chiffrage porte déjà les deux recettes ; son
hypothèse n° 1 et sa table E attendent l'étape 9. Par quoi commencer :
l'étape 3, l'AVPF, qui n'attend rien.

*Le 9 novembre 2026, le propriétaire a tranché, ligne à ligne, ce que
deviennent les recettes de la retraite sous la proposition (décisions 47, 57,
79 à 81, 88, 91 à 99, 103 et 104 de `docs/feuille_de_route_programme.md` ;
note `2026-11-09-qui-finance-quoi.md`). Rien n'en était au modèle. Cette
session écrit le plan du portage et en fait la première étape. Elle a relu la
note, les décisions, `SoldeAnnuel.ressources_de` et `postes_ressources`
(`src/retraite_notionnelle/cout.py`), et le rapport à la Commission des
comptes de la sécurité sociale d'octobre 2026, sur le document.*

*Lire les chiffres.* **(publié)** : lu à sa source, citée. **(dépôt)** : sorti
du modèle ou d'un fichier du dépôt, au commit `3591bdc`. **(calcul)** : fait
par la session, posé ici. Montants en milliards d'euros courants.

## Où en est le modèle

Le coût du scénario 6, en 2026, en points de PIB (dépôt,
`SoldeAnnuel.postes_ressources("notionnel_liberal")`) :

| Poste | Droit en vigueur | Proposition |
|---|---:|---:|
| Cotisations | 9,16 | 7,69 : 18 % de toute l'assiette |
| Contribution d'équilibre de l'État | 1,63 | 0 |
| Subventions d'équilibre | 0,25 | 0 |
| Impôts et taxes affectés | 2,14 | 0 |
| Transferts | 0,54 | 0,17 : l'Unédic et les autres, sans la branche famille |
| Autres produits | 0,23 | 0,23 |
| **Total** | **13,96** | **8,10** |
| Solde | − 0,16 | − 2,19 |

Quatre choses s'y lisent, qui commandent le plan.

1. **Le poste des impôts affectés part en entier.** La CTA est donc déjà
   ôtée (décision 88), comme les alcools (92) et tous les impôts que la table
   « impôt par impôt » retire : le coût n'a rien à changer pour eux. Ce que
   devient leur moitié (94, 103, 104) ne regarde pas la caisse des retraites :
   c'est la fiche de paie et le chiffrage (étapes 6 et 9).
2. **La TVA de l'Agirc-Arrco part avec le poste**, contre la décision 79.
3. **La branche famille est retirée en entier**, AVPF comprise, contre la
   décision 57 ; et la couche `comptes_notionnels.yaml` neutralise encore
   l'AVPF au compte (`vise: avpf`). Recette et droit vont ensemble.
4. **Les cotisations sont 18 % de toute l'assiette**, comme si aucun
   allègement n'existait. La décision 96 le fonde : l'État verse ce que les
   allègements effacent. Le coût n'a rien à y changer ; reste à dire combien
   l'État verse (étape 7).

## Le plan

Une étape par session, chacune son test tiré de la source, vu rouge avant le
code. L'ordre met d'abord ce qui n'attend aucune réponse.

| | Étape | Zone | Le test, tiré de | Attend |
|---|---|---|---|---|
| 1 | **Faite.** La part de TVA de l'Agirc-Arrco, en donnée | données | CCSS d'octobre 2026, fiche 1.6, p. 67 | — |
| 2 | La TVA de l'Agirc-Arrco au coût du scénario 6 | modèle (`cout.py`) | la série de l'étape 1 : 11,1 Md€ en 2026 | question 1 |
| 3 | L'AVPF gardée : la recette, et le droit au compte | modèle, couches, données | 5,04 Md€ cotisés en 2025 (dépôt, `transferts_retraite.csv`) ; 4,39 servis en 2024 (publié, à saisir) | — |
| 4 | Le point de LVT des retraites | données, puis modèle | terrains privés, 6 091 Md€ fin 2025 (publié, Insee) ; le calcul de la note du 7 novembre, à refaire au dépôt | question 2 |
| 5 | Le chômage et la maladie au compte, payés par leurs assurances | modèle, couches | 13,1 et 2,3 Md€ en 2025 (publié, fiche 4.5) | le prix, que l'étape chiffre |
| 6 | `restitution.py` et la fiche de paie, « impôt par impôt » | portage d'abord (`moteur/js`), puis son jumeau | la table de la note : 5,3 sur 10,6 ; 3,3 sur 6,6 ; 1,47 et 3,3 points | — |
| 7 | Ce que l'État verse pour les allègements, au taux unique | modèle (fiche de paie), données | 19,8 Md€ effacés à la branche vieillesse en 2026 (publié, fiche 1.6), 11,1 à l'Agirc-Arrco (calcul, étape 1) | — |
| 8 | Les deux écarts restants de « 1.3 » | données | COR, tableau 2.2 : 277,0 Md€ de cotisations en 2025 ; CCSS, p. 67 | — |
| 9 | `docs/chiffrage_plf.md` : l'hypothèse n° 1 et la table E | chiffrage | la table « impôt par impôt » | étapes 2 à 7 |

Ce que chaque étape fait, et ce qu'elle ne fait pas.

**2. La TVA au coût.** Le scénario 6 reçoit, à compter de la bascule, la
compensation de l'Agirc-Arrco : la série de l'étape 1 de 2025 à 2027,
rapportée au PIB du modèle (0,36 point en 2026 : 11,14 ÷ 3 065, calcul), puis
à part de PIB constante, les allègements suivant le SMIC. Sous la réponse A
de la question 1, elle s'ajoute au total ; sous B, elle se lit dans la ligne
des cotisations, et le total ne bouge pas. `scripts/lectures_decision_29.py`
la compte encore pour 0,23 point (`TVA_RETRAITES`) : à lire dans la série
sous A, à mettre à zéro sous B. Au site, sans y toucher : la ligne
`impots_tva` s'y nomme « Dont TVA à taux unique », et trois affirmations
disent qu'aucun impôt n'entre au régime (`cout.ligne_a_ligne`,
`trois_postes_disparaissent`, `recettes_trois_reactions`) ; à déclarer au
catalogue, pour la session du site.

**3. L'AVPF.** La branche famille continue de cotiser : la ligne `cnaf_avpf`
reste au scénario 6, 0,17 point de PIB (dépôt), 5,3 Md€ en 2026 (publié).
Mais la recette suit le droit : la couche du scénario 6 cesse de neutraliser
l'AVPF au compte (le portage d'abord, son jumeau ensuite), et le coût garde
la part des pensions servies qu'elle a ouverte, que la grille ne voit pas —
un seul cas type a des enfants. La note des enfants la chiffre à côté à
0,185 point de dépense en moyenne (calcul, `2026-11-07-enfants-regle-par-regle.md`) :
garder la recette sans la dépense embellirait le solde de 5 Md€ par an. La
dépense demande une donnée de plus, les pensions d'AVPF servies.

**4. La LVT.** Un point de la valeur des terrains privés aux retraites, dès
la bascule (décisions 80 et 81), sans abattement ni plafonnement, remis à
plus tard. Le calcul de la note du 7 novembre est resté hors du dépôt : il y
entre en donnée, avec ses sources, et le coût en reçoit une ligne. La valeur
retenue est la question 2.

**5. Le chômage et la maladie.** Les périodes sont portées au compte, et
leurs assurances cotisent (décisions 97 et 99). Le prix n'est pas tranché :
l'étape chiffre les deux, 18 % de l'allocation et le forfait d'aujourd'hui
(13,1 et 2,3 Md€ en 2025, publié), les rend au propriétaire, et ne porte au
coût que celui qu'il choisit. Dans le coût, c'est la ligne `fsv_cotisations`
que le scénario 6 retire aujourd'hui avec l'ancien fonds de solidarité.

**6. La fiche de paie.** La règle du 20 septembre (`part_rendue_aux_salaires`)
cède à la table : plus de baisse de la CSG sur les salaires ; la taxe sur les
salaires et le forfait social baissent de moitié sur leur part retraite au
lieu de disparaître ; la CSG sur les pensions baisse de 1,47 point, celle du
capital de 3,3. La hausse des fonctionnaires reste où elle est, au
simulateur, hors de la page Coût (décision 98).

**7. Les allègements.** La note ne les connaît qu'entre 24,3 et 30,9 Md€. Le
montant exact se calcule par la fiche de paie du simulateur, qui applique
déjà la réduction au taux unique, sur la dispersion des salaires du dépôt. Il
ne change pas le coût, qui encaisse ses 18 % ; il dit ce que l'État verse, et
va au propriétaire, puis au chiffrage.

**8. Les écarts de « 1.3 ».** Le premier, la TVA de la Cnav, nulle, est réglé
par l'étape 1 : la donnée le dit. Restent la structure des ressources du COR
appliquée à un total qui exclut les produits financiers, et la réduction
générale dégressive unique de 2026, qui déplace une dizaine de milliards des
cotisations vers les impôts. Les deux déplacent les postes du droit en
vigueur sans toucher à ses règles ; ils sont à la session des données.

**9. Le chiffrage.** L'hypothèse fragile n° 1 de `docs/chiffrage_plf.md`,
prose écrite à la main, dit ce que devient chaque ligne ; la table E,
`python scripts/chiffrage_plf.py`.

## L'étape 1 : la part de TVA de l'Agirc-Arrco, en donnée

Aucune source lue ne publie ce que l'Agirc-Arrco reçoit. Le rapport
d'octobre 2026 publie ce que la réduction générale efface hors des régimes
de base — assurance chômage, retraite complémentaire, FNAL :

| En M€ | 2024 | 2025 | 2026 (p) | 2027 (p) |
|---|---:|---:|---:|---:|
| Régimes de base | 26 681 | 26 529 | 54 301 | 51 722 |
| Hors régimes de base | 12 671 | 12 587 | 18 910 | 18 011 |
| Ensemble | 39 352 | 39 115 | 73 211 | 69 733 |

(publié, fiche 1.6, tableau 2, p. 67 ; la réduction générale jusqu'en 2025,
la réduction générale dégressive unique ensuite, qui absorbe les baisses de
taux de maladie et de famille : la première ligne ne se compare pas d'un
dispositif à l'autre, la deuxième si.)

Et il dit ce qu'est la TVA de l'Agirc-Arrco : « L'Agirc-Arrco et l'Unédic
doivent être compensées des pertes de recettes liées à l'intégration des
cotisations et contributions patronales de retraite complémentaire et
d'assurance chômage à la réduction générale […]. Cette compensation est à
l'euro près pour l'Agirc-Arrco […]. À cette fin, l'Acoss est affectataire de
recettes de TVA » (publié, synthèse, p. 15).

La part de l'Agirc-Arrco se déduit des taux que la réduction efface : 4,72
points de cotisation et 1,29 de contribution d'équilibre général, 6,01, sur
10,2 hors des régimes de base avec l'assurance chômage (4,05, puis 4,00) et
le FNAL (0,10). Soit 0,589 (calcul) :

- 2025 : 0,589 × 12,587 = **7,4 Md€** ; 0,25 point de PIB (7,42 ÷ 2 991) ;
- 2026 : 0,589 × 18,910 = **11,1 Md€** ; 0,36 point (11,14 ÷ 3 065) ;
- 2027 : 0,589 × 18,011 = **10,6 Md€**.

Le calcul de la note est donc confirmé sur sa source. Deux recoupements, et
deux limites :

- le saut de 2026, 3,7 Md€ (calcul), recoupe l'effet de la réduction unique
  sur les cotisations de l'Agirc-Arrco, 3,8 (publié, tableau 3, p. 67) ;
- les deux parts du tableau somment à son ensemble, au million près ;
- au-delà de cinquante salariés le FNAL vaut 0,50 point, et la part tombe à
  0,57 : 10,8 Md€ en 2026 au lieu de 11,1 (calcul) ;
- la TVA ne paie pas toute la compensation : le régime général a complété de
  1,0 Md€ en 2025, Unédic comprise, et de 0,2 attendu en 2026 (publié, p. 15).

Au dépôt : `data/reference/macro/allegements_hors_regimes_de_base.csv`, son
jeu `dss_ccss_allegements_hors_base` au manifeste,
`src/retraite_notionnelle/donnees/compensation_agirc_arrco.py`, qui pose le
calcul, et `tests/test_compensation_agirc_arrco.py`, sept tests. Rien d'autre
ne bouge : aucun résultat du modèle ni du site.

## Ce que le propriétaire tranche

### 1. La TVA de l'Agirc-Arrco s'ajoute-t-elle à ce que l'État verse pour les allègements ?

**Ce qui se passe aujourd'hui.** Pour un salarié au SMIC, 1 823 € brut par
mois, l'employeur devrait 16,58 points de cotisations de retraite : 193 € à
la Cnav, 110 € à l'Agirc-Arrco. La réduction générale efface les deux. La
fraction de TVA existe pour une seule chose : rendre à l'Agirc-Arrco ces
110 €, à l'euro près (publié).

**Ce que les décisions disent.** La décision 96 : l'État verse à la retraite
la cotisation que les allègements effacent, soit toute la part patronale du
taux unique, 13,05 points, 238 € par mois pour ce salarié. La décision 79 :
la retraite garde la part de TVA qu'elle reçoit. Les deux décisions paient
la même chose, la cotisation effacée de ce salarié ; la note du 9 novembre
ne l'avait pas vu, et sa table les additionne.

**La question.** La TVA s'ajoute-t-elle aux 238 €, ou en fait-elle partie ?

| | A. Elle s'ajoute (la table confirmée, telle qu'elle est écrite) | B. Elle en fait partie |
|---|---|---|
| Pour ce salarié, la retraite reçoit de l'État | 238 € et 110 € de TVA : 348 € par mois | 238 €, dont 110 € par la TVA |
| Porté à son compte | 328 € (18 % de 1 823 €) dans les deux cas | 328 € |
| Recettes de la retraite en 2026 | + 11,1 Md€, 0,36 point de PIB : le solde passe de − 2,19 à − 1,83 point | inchangées : − 2,19 |
| L'État verse à la retraite | 35,4 à 42,0 Md€ | 24,3 à 30,9 Md€ |
| Il reste à l'État, des impôts retirés | + 4,3 à − 2,3 Md€, comme la table l'écrit | + 15,4 à + 8,8 Md€ |
| Solde de toutes les administrations | le même | le même |

Sous A, 110 € par mois entrent à la caisse pour ce salarié sans être portés à
aucun compte : la TVA devient une recette de la caisse, comme la LVT. Sous
B, la TVA est le moyen par lequel l'État paie une partie des allègements, et
la caisse ne touche que ses 18 %. Les montants sont ceux de la note, à
l'étape 7 de les préciser (calcul : 24,3 + 11,1 = 35,4 ; 30,9 + 11,1 = 42,0 ;
28,6 − 24,3 + 11,1 = 15,4 ; 28,6 − 30,9 + 11,1 = 8,8).

### 2. Quelle valeur de la LVT le coût retient-il ?

**Ce qui se passe aujourd'hui.** La décision 80 donne une fourchette : le
point des retraites rapporte 36 à 43 Md€ aux valeurs de 2025, 1,2 à 1,4
point de PIB, selon ce que les terrains rapportent (2,5 à 4 % par an) ; le
coût, lui, affiche un solde par an, donc un nombre.

**La question.** Lequel ?

| | Basse : 1,2 point | Centrale : 1,3 point | Haute : 1,4 point |
|---|---|---|---|
| Recette en 2026 (calcul, sur 3 065 Md€ de PIB) | 36,8 Md€ | 39,8 Md€ | 42,9 Md€ |
| Solde de la retraite en 2026, sans la TVA (dépôt, calcul) | − 0,99 point | − 0,89 point | − 0,79 point |
| Ce que le point des retraites prélève, par ménage et par an (calcul, 30 millions de ménages) | 1 230 € | 1 330 € | 1 430 € |

L'autre point, celui des communes, remplace la taxe foncière, 42,9 Md€ en
2024 (décision 80) : le ménage ne paie de plus qu'aujourd'hui que le point
des retraites.

Ce que la session propose, faute de réponse : la valeur centrale pour le
solde affiché, la même que `scripts/lectures_decision_29.py` a prise au
chantier 1, et la fourchette écrite à côté. La recette suit le PIB chaque
année. L'abattement de la résidence principale et le plafonnement, remis à
plus tard, la baisseront.

## Ce qui reste

- Les étapes 2 à 9, dans l'ordre du plan ; l'étape 3 n'attend rien.
- À la session du site, quand les pages seront libres : le libellé « Dont
  TVA à taux unique » de la ligne `impots_tva`, et les affirmations que les
  étapes 2 à 4 démentiront ; chaque étape les déclare au catalogue.
- Le montant que l'Agirc-Arrco reçoit vraiment, quand ses comptes de 2025
  le publieront autrement qu'en image : la série n'en est qu'un calcul.
