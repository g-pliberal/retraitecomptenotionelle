# La part de TVA gardée et le point de LVT, portés au coût du scénario 6

*Le 9 novembre 2026, le propriétaire : « Il faut qu'on s'occupe de la TVA et
de la LVT. Il faut qu'on ajoute ces recettes à notre évaluation des coûts. »
Les décisions 79 à 81 étaient prises depuis le 7 novembre, et les deux
recettes ne se comptaient qu'à côté du modèle
(`scripts/lectures_decision_29.py`). Cette session les porte au coût agrégé
(`cout.py`), au chiffrage (`docs/chiffrage_plf.md`) et à la page Coût. Ce
sont les étapes 2 et 4 du plan qu'une autre session écrivait le même soir
(`2026-11-09-recettes-au-modele.md`), dont elle reprend la série de la TVA
et les deux questions, que le propriétaire a tranchées.*

## Ce que le propriétaire a tranché

Aux deux questions du plan, posées en choix (décisions 105 et 106 de
`docs/feuille_de_route_programme.md`) :

- **La TVA s'ajoute** : « Elle s'ajoute ». Le coût prélève 18 % sur toute
  l'assiette, comme si l'État compensait tous les allègements de cotisations
  (décision 96) ; la TVA de l'Agirc-Arrco, qui est aujourd'hui cette
  compensation pour la caisse, entre au régime en plus. Comptée dans ce que
  l'État verse, elle aurait laissé le solde moins bon de 0,36 point de PIB.
- **La LVT à sa valeur centrale** : « Centrale : 1,3 point », pour des
  terrains qui rapportent 3 % par an.

## Ce qui est fait

**La part de TVA gardée (décision 79).** Le droit tranche ce que la décision
laissait « à chiffrer » : l'article L. 131-8, 9°, du code de la sécurité
sociale, lu au texte en vigueur, n'affecte aucune TVA à la branche
vieillesse. La part des retraites est la seule compensation de la réduction
générale à l'Agirc-Arrco (7° de l'article L. 225-1-1). Le coût la lit dans
la série que le dépôt tient depuis le même soir
(`donnees/compensation_agirc_arrco.py`) : 11,1 Md€ en 2026 et 10,6 en 2027,
rapportés au PIB de leur année, 0,36 puis 0,34 point ; au-delà, la part de
PIB de 2027 est tenue (`donnees/tva.py`, `TvaGardee`).

**Le point de LVT (décisions 80, 81 et 106).** Le calcul de l'étude du
7 novembre est au modèle (`donnees/lvt.py`), sur des données recopiées de
leur source : les terrains bâtis des ménages et des sociétés fin 2025,
6 091 Md€ (Insee) ; la taxe foncière de 2024, 42,9 Md€ (Fipeco, comptes
nationaux), 0,32 % de l'immobilier privé. Le prix du terrain devient
P₀ × y ÷ (y − 0,32 % + t). À 2 % et pour un rendement locatif du terrain de
3 %, il baisse de 36 %, la taxe rapporte 78 Md€, et le point des retraites
39 Md€ : 1,31 point du PIB de 2025, que le coût tient constant, dès la
bascule. Le tableau de l'étude se refait au milliard près
(`tests/test_recettes_affectees.py`).

**Où elles entrent.** Au régime de la proposition, au poste des impôts et
taxes affectés, chacune sur sa ligne (`SoldeAnnuel.tva_gardee_de`, `lvt_de`),
à compter de la bascule, et à aucun autre système. La garantie vieillesse
reste à la charge de l'impôt général : c'est la base de la page Coût, celle
des tableaux du 8 novembre, et le solde garantie comprise est le même de
quelque côté qu'on les range. Quatre paramètres les règlent
(`tva_des_retraites_gardee`, `taux_lvt`, `taux_lvt_retraites`,
`rendement_locatif_terrain`).

**Ce qui suit.** Le chiffrage porte la ligne de la LVT au fait central et
aux arbitrages, la colonne des deux recettes aux prélèvements, un paragraphe
daté et la limite n° 13. La page Coût les nomme : deux lignes au tableau
poste par poste, le nœud « Terrain et TVA » au schéma des flux, la phrase de
la carte et de deux notes ; l'accueil dit un excédent et des réserves là où
il disait un besoin et une dette. Trois comparaisons les tiennent à l'écart,
comme la TVA à taux unique avant elles : le coût des 18 %
(`solde_fusion.py`), les postes écartés (`postes_ecartes.py`), les lectures
de la décision 29, qui les comptaient à la main.

## Ce que cela déplace

Variante rétroactive, taux de 18 %, en points de PIB, sur le modèle du jour,
garantie dégressive comprise :

| | Sans elles | Avec les deux recettes |
|---|---:|---:|
| Recettes de la proposition en 2026 | 8,10 | 9,77 |
| Solde du régime en 2026 | −2,19 | −0,53 |
| Solde garantie comprise en 2026 | −2,79 | −1,12 |
| Écart au droit en vigueur en 2026, garantie comprise | −2,63 | −0,96 |
| Coefficient d'équilibre en 2026 | 0,79 | 0,95 |
| Solde moyen du régime, 2026-2070 | −1,44 | +0,20 |
| Première année d'équilibre du régime | 2070 | 2053 |
| Dette du régime en 2070 | 103 | une réserve de 6 |

**Un fait à voir en face.** Avec le pilier obligatoire, la proposition
prélève désormais pour la retraite plus que le droit en vigueur
(`docs/chiffrage_plf.md`, tableau des prélèvements) : le point de LVT des
retraites en fait 1,3 point de PIB, et ne remplace aucun impôt des
retraites, l'autre point remplaçant la taxe foncière.

## Ce qui reste à faire

- **La suite du plan** de `2026-11-09-recettes-au-modele.md` : l'AVPF (3),
  le chômage et la maladie (5), la restitution (6), qui rend encore aux
  salaires la moitié de tout le poste des impôts affectés, part de TVA
  gardée comprise, contre la décision 94 ; ce que l'État verse (7), les
  écarts du compte (8), l'hypothèse n° 1 et la table E du chiffrage (9).
- **Le site**, au chantier 9 : le texte de la page Coût dit encore « trois
  postes disparaissent », et la note de la restitution l'ancienne règle.
- **L'abattement et le plafonnement de la LVT**, remis à plus tard par le
  propriétaire ; le rendement locatif du terrain, que rien ne mesure.
- **L'épaisseur des schémas de flux** est passée de 240 à 180 pour que les
  deux tiennent dans un écran de bureau avec le nœud de plus ; les budgets
  de mots de la page Coût, de 946 à 962 et de 33 293 à 33 312.
- `scripts/lectures_decision_29.py` lit les deux recettes au modèle : ses
  taux des lectures A et B sont à refaire
  (`python scripts/lectures_decision_29.py`).
- **Un test rouge qui n'est pas de cette session** :
  `tests/test_parcours.py`, section « Programme », cite « 1 600 € » et
  « 100 % » que l'accueil n'affiche plus depuis sa réécriture (action 189).
