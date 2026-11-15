# Les 18 % du salarié du privé au modèle : déjà au compte, et la tranche 2 de l'Agirc-Arrco ramenée à 18 %

Le 14 novembre 2026, une session du modèle, sur la proposition seule, ouverte
pour porter la décision 111 (« 18 % dès le premier jour ») au modèle.

## Ce que la session a trouvé

**Le moteur d'une carrière crédite déjà 18 % dès la bascule**, pour tout le
monde, au scénario 6 (`taux_historiques_puis_uniforme`, `tauxUnifie` dans
`moteur/js/compte.js`). Il n'avait jamais porté les 25,83 % de la décision 48
(note `2026-11-09-pensions-qui-montent.md`, tableau des décisions non
portées). Sous le plafond, la décision 111 est donc ce qu'il calcule : que le
régime général prenne 10,13 % et l'Agirc-Arrco 7,87 % ne change rien au compte
de l'assuré, seulement qui encaisse. Le coût réunit encore toutes les caisses
dès la bascule : les quelque 50 Md€ par an que le régime général perd,
l'Agirc-Arrco les garde, et le solde d'ensemble ne bouge pas.

**Au-dessus du plafond, un écart restait** : l'Agirc-Arrco y prélève seule
21,59 % (tranche 2, 17 % × 127 %, sans la CEG), plus que 18 %. Posée au
propriétaire, la question a reçu « 18 % partout » (décision 139) : elle ramène
sa tranche 2 à 18 % dès la bascule, et le régime général n'y prend plus rien.

## Ce qui est écrit

`integration_complementaires.py` : `TAUX_MAXIMAL` (18 %), et
`ContributionsSupprimees.tranche_2_meur`, ce que la tranche 2 perd au-delà de
18 %, 4 304 M€ sur les assiettes de 2024 ; la part retirée à l'Agirc-Arrco
passe de 19,18 % à 23,76 % de ce qu'elle prélève. Ses réserves s'épuisent
en 2030, non plus en 2032 : 0,16 point de PIB de plus perdu chaque année. Le
test d'abord, la valeur posée à la main dans
`tests/test_integration_complementaires.py`.

Le moteur d'une carrière ne change pas : il crédite 18 % sur tout le salaire.

## Ce qui reste

- Les années d'intégration ne sont lues par aucun autre calcul : l'étape 2 de
  `2026-11-07-complementaires-au-modele.md` (le moteur) et l'étape 3 (le coût
  qui sépare les caisses jusqu'à leur intégration, puis le site) les
  prendront. L'étape 2 n'a plus à faire payer 25,83 % au salarié du privé :
  sous les décisions 111 et 139, il verse 18 % dès la bascule, et seuls ses
  droits acquis à l'Agirc-Arrco jusqu'en 2030 restent à porter.
- Le partage des recettes entre le régime général et l'Agirc-Arrco, que
  l'étape 3 chiffrera quand le coût séparera les caisses.
- Les notes qui disent « 2032 » pour l'Agirc-Arrco datent d'avant la
  décision 139 ; elles restent vraies à leur date.
