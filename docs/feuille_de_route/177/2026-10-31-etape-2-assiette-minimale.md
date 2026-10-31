# Étape 2 : l'assiette minimale des indépendants, avant 1985 et en 2022

**Le 31 octobre 2026, ce qui est fait.** Les deux écarts que
`ECARTS_ASSIETTE_MINIMALE` tenait depuis l'étape 2 de l'action 175 sont
corrigés, un par commit, chacun d'abord retiré de la liste et vu rouge ; la
liste est vide.

1. *De 1973 à 1984.* Le texte qui fixe le minimum avant la codification de
   1985 est l'article 2 du décret n° 73-76 du 22 janvier 1973
   (LEGIARTI000006765785, en vigueur du 24 janvier 1973 au 21 décembre
   1985), lu dans l'index LEGI : « Toutefois, le montant de la cotisation
   annuelle ne peut être inférieur à celui de la cotisation qui serait due au
   titre d'un revenu égal à 200 fois le montant horaire du salaire minimum de
   croissance en vigueur le 1er janvier de l'année considérée ». D. 633-2 le
   reprend mot pour mot en 1985 (LEGIARTI000006737877), et ses articles 1er,
   5, 6, 9, 10, 16 et 21 n'ajoutent aucune condition au minimum. La ligne des
   artisans, commerçants et gérants de débit de tabac de
   `assiette_minimale_independants.csv` commence donc en 1973 ; la série
   redonne les douze montants de la caisse, de 910 F à 4 556 F. L'index JORF
   ne garde de la loi n° 72-554 du 3 juillet 1972 que des articles vides :
   c'est LEGI qui porte le décret, texte non codifié, article par article.
2. *En 2022.* L'article 1er du décret n° 2022-1438 du 16 novembre 2022
   (JORFARTI000046566175), relu au JORF avec sa notice : « Par dérogation aux
   articles D. 633-2 et D. 642-4 [...], la cotisation annuelle due au titre
   de l'année 2022 [...] ne peut être calculée sur une assiette inférieure à
   4 758 euros », de quoi « valider trois trimestres ». La série ne savait
   dire un montant qu'en heures du Smic ou en part du plafond : elle prend une
   colonne `euros`, que lisent `AssietteMinimale.montant` et son portage,
   `montantAssietteMinimale` ; le paquet du site passe en version 35, sa
   structure ayant changé. Les lignes de 2016 à 2022 des deux familles
   s'arrêtent en 2021, et 2022 a la sienne. Le décret ne redit ni la
   condition de quatre-vingt-dix jours d'affiliation de D. 633-2 et D. 642-4,
   ni leur refus du prorata : la série garde l'une et l'autre, une lecture
   que la fiche met à relire.

`test_l_assiette_minimale_des_independants_est_celle_que_la_caisse_publie`
redonne désormais la table de la caisse de 1973 à 2026, sans écart. Deux cas
posés à la main depuis les textes, dans `tests/test_independants.py`, se
jouent dans les deux moteurs : l'artisane et la commerçante à 100 € par an de
1970 à 1989, l'artisane et la libérale à 3 000 € par an de 2020 à 2024 ; ils
passent par `_deux_moteurs`, que le test des dispenses reprend.

**Ce que le calcul en reçoit.** Mesuré au moteur Python avant et après
l'étape : l'artisane née en 1945, à 100 € par an de 1970 à 1989 et partie à
soixante-cinq ans, valide 19 trimestres au lieu de 7, et la CANCAVA lui sert
782 € par an au lieu de 230 € ; le commerçant né en 1950, à 300 € par an de
1973 à 1984 puis à 15 000 €, valide 121 trimestres au lieu de 114, et le RSI
lui sert 5 824,21 € au lieu de 5 487,27 €. En 2022, l'artisane née en 1962, à
3 000 € par an depuis 1990, valide 76 trimestres au lieu de 75, et son régime
général sert 940,15 € au lieu de 927,54 € ; la libérale, 45 au lieu de 44.
Des 913 témoins de simulation, refaits sur le poste, un seul bouge,
`dispense_liberale_pensionnee` (+0,25 % au scénario 1, son trimestre de
2022), et aucune des 85 pages ; GitHub les refait après l'envoi.

**Vu en chemin, non corrigé.**

- L'édition des DOM du barème de la caisse garde pour 2022 11,5 % du
  plafond, 4 731 € : le décret, qui vise tous les indépendants de L. 631-1 et
  L. 640-1, n'excepte pas les DOM, et le modèle y applique 4 758 €. Le test
  des DOM le déclare (`ECARTS_ASSIETTE_MINIMALE_DOM`), la limite
  « indépendants des DOM » le dit ; à reprendre avec l'étape 4.
- L'article 6 du décret n° 73-76, dans sa rédaction du 1er janvier 1978,
  assied la cotisation de l'année de début d'activité sur un revenu
  forfaitaire d'un tiers du plafond, et la provisionnelle de l'année suivante
  sur la moitié, que l'article 9 permet d'ajuster sur demande : le
  prédécesseur de D. 633-6, pour l'étape 5 (l'assiette d'avant 2007).
- Le commentaire de la série disait le modèle ignorant des deux dispenses de
  D. 642-4, l'activité libérale non principale et le libéral pensionné, que
  `dispenses_assiette_minimale.yaml` porte de 2004 à 2015 : récrit.

**L'étape est faite.** La suite : l'étape 3, Mayotte (la fiche
`cssm_mayotte`, à faire lire `mayotte_smig_et_plafond.csv`).
