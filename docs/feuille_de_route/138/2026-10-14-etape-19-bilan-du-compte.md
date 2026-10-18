# Étape 19, première partie : le bilan du compte notionnel, à la manière suédoise

**Reprise, au 18 octobre 2026.** Fait : le bilan du compte, en indicateur
(`bilan_compte.py`, 14 octobre) ; la carrière heurtée d'Osiris, écrite et
éprouvée sur le droit, hors des deux grilles (`CARRIERE_HEURTEE`, 18 octobre).
Au propriétaire : le biais des cotisants de moins de 50 ans de `cout.py`
(« Trouvé en chemin ») ; le poids de la carrière heurtée, qui fait partir la
grille trop tard à toute part de la Cnav, faute des départs anticipés du privé
(trois voies, note du 18 octobre). À une session des pages : le bilan sur la
page Coût, et « treize carrières » si la grille s'agrandit. Coupés le 14 :
l'incertitude, la rétro-projection, la solidarité de la Cnav, `d × r`.

**La demande.** Session du 14 octobre 2026, la n° 12 de dix-neuf : « action
138, étape 19, jamais commencée […] Commence par le bilan du compte
notionnel, une grandeur que le site ne donne pas : la durée de rotation,
l'actif de cotisation, les réserves et leur rendement, le taux de cotisation
d'équilibre, à la manière du bilan annuel du système suédois. » Les sessions
4, 10 et 11 touchant aussi au Coût, rien n'est écrit dans `cout.py` ni dans
les pages.

**Ce que le registre en dit.** Trois points au chantier 138.19, tous trois
repris par cette partie : l'indice d'équilibre suédois comme indicateur (le
modèle de Pensionsmyndigheten, SFB 58:14-20, rapport orange 2025 : actif de
cotisation 11 370 Md SEK, fonds 2 234, dette 11 859) ; le fonds tampon et son
rendement, que la page Coût laisse hors du calcul ; le taux de cotisation
d'équilibre du modèle de l'OIT, `C = d × r`. Les quatre autres points du
chantier — la rétro-projection de l'Ageing Report, l'incertitude de
Monte-Carlo, la carrière heurtée d'Osiris, la solidarité de la Cnav — restent
`a_reprendre`.

**Ce qui est fait.**

- *La durée de rotation*, à la forme de Settergren et Mikula (2005), en coupe
  une année : l'âge moyen des pensions servies, pondéré par leurs montants,
  moins celui des cotisations versées. Les profils par âge viennent de la
  grille, pesés comme les masses de `cout.py` (effectifs de l'INSEE pour les
  cohortes, cotisants ou retraités des caisses pour les cas types, pension
  revalorisée selon la règle de chaque système, comme l'engagement). La
  pyramide du dépôt s'arrêtant à 50 ans, un cotisant plus jeune est compté
  par l'effectif de sa génération à ses 50 ans (`effectif_cotisant`).
- *Les réserves*, saisies du rapport annuel du COR de juin 2026 (partie 2,
  chapitre 3, tableau 2.3, § 3.1 à 3.3) dans `reserves_retraite.csv`, source
  `cor_reserves_systeme_retraite` : 213,8 Md€ dans les régimes fin 2024, 223,9
  fin 2025, plus le FRR (20,4 puis 20,7), soit 244,6 Md€ et 8,2 % du PIB ; la
  dette de la Cades imputable aux retraites, 29,3 Md€. Le rendement comptable
  de 2025, les produits financiers nets (5,1 − 1,3 = 3,8 Md€, § 1.1) sur le
  stock de fin 2024 : 1,6 %.
- *La dette* est l'engagement acquis de la page Coût
  (`calculer_engagements`), au prorata temporis et actualisé au rythme du PIB.
- *Les taux d'équilibre* : la dépense sur l'assiette des revenus d'activité
  (tout payé par l'assiette), et le taux de cotisation qui équilibre l'année,
  les autres ressources gardées — le levier du prélèvement de `leviers.py`
  (138.3), limité aux cotisations.

**Ce que cela donne, fin 2025** (`python scripts/bilan_compte.py`, réglages
de référence), en part du PIB :

| Système | Durée de rotation | Actif de cotisation | Dette | Ratio | Taux d'équilibre, tout | Taux de cotisation d'équilibre |
|---|---:|---:|---:|---:|---:|---:|
| 1. Système actuel | 29,3 ans | 316 % | 497 % | 0,65 | 33,2 % | 25,8 % |
| 2. Rétroactif, part salariale | 29,5 ans | 319 % | 161 % | 2,03 | 8,6 % | 3,6 % |
| 4. Rétroactif, part patronale | 29,3 ans | 316 % | 389 % | 0,83 | 21,2 % | 16,2 % |
| 6. La proposition | 29,4 ans | 317 % | 355 % | 0,92 | 21,2 % | 16,2 % |

Les cotisations valent 10,8 % du PIB (25,4 % de l'assiette), versées à 44,8
ans en moyenne ; les pensions sont servies à 74,1 ans. La durée de rotation
est celle de la Suède, qui publie un peu plus de trente ans. Le système actuel
porte une dette que ses cotisations ne couvrent qu'aux deux tiers, réserves
comprises : c'est ce que dit, en stock, le déficit que la page Coût dit en
flux. Les scénarios 3 et 5 sont, en 2025, avant leur bascule.

**Les limites, à dire avec le chiffre.** La forme en coupe suppose une
structure par âge stable, comme le bilan suédois (rapport orange 2025, note 3)
; la France de 2025 a ses générations nombreuses à la retraite, qui allongent
l'âge des pensions. La dette au prorata temporis n'est pas la somme des
comptes notionnels que la Suède met au passif : c'est la convention commune
aux six systèmes, et le niveau de l'engagement dépend du taux d'actualisation
(`EngagementAcquis.sensibilite`). Les réserves sont les mêmes pour tous les
systèmes, le programme ne disant pas ce qu'il en ferait ; la pension servie ne
compte pas la réversion, que la dette compte en partie.

**Trouvé en chemin, pour le propriétaire.** `_masses_cotisations` de `cout.py`
pèse les cotisants de la grille par `Population.effectif`, qui rend zéro sous
50 ans : la recette de la page Coût ne voit aucun cotisant de moins de 50 ans.
Le rapport de recettes (convention `rapport`) et surtout le facteur d'assiette
du scénario 6 (convention `assiette`, celle de la page) en sont faussés : le
second vaut 1,025 au lieu de 1,012 environ (1,033 au lieu de 1,013 en 2030 ;
1,025 au lieu de 1,018 en 2060), parce que les années de travail que l'âge
légal ajoute après 62 ans sont rapportées aux seules carrières d'après 50 ans.
La recette de la proposition en est surestimée d'environ 1,3 %, de l'ordre de
0,1 point de PIB par an. Le correctif tient en une ligne — peser par
`effectif_cotisant`, à déplacer dans `donnees/population.py` — mais il déplace
les chiffres de la page Coût, où travaillent d'autres sessions ce jour :
laissé au propriétaire.

**Ce qui reste**, outre le bloc « Reprise » : la décomposition `d × r` en
têtes, la prime moyenne sur une période et le taux qui tient un ratio de
réserve cible, que le modèle de l'OIT fait aussi ; les réserves projetées, et
leur emploi contre les déficits ; le bilan d'une année projetée, à la dette
calculée à cette date.
