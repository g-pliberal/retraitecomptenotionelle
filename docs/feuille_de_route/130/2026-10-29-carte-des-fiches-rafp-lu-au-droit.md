# La carte des fiches : le RAFP lu au droit, premier lot

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après les
cinq lots qui ont donné à toute fiche son code et ses régimes
(`130/2026-10-29-carte-des-fiches-dernier-lot.md`). Celle-ci, de l'action 130 :
un premier lot des 106 fiches à lire au droit — leurs versions, leur domaine,
leur étape, ce qu'elles lisent et écrivent, leurs dates qui décident —, selon
`docs/veille_droit.md`. Le lot pris est un régime, le RAFP, dont les deux
dernières fiches, `rafp_assiette_plafond` et `rafp_beneficiaires`, n'étaient
pas mûres : toutes les siennes le sont désormais. Aucun chiffre du modèle ne
bouge, ni le paquet du site, qui ne lit aucune des deux.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; l'index LEGI récupéré, mis à jour
  jusqu'à l'incrément du 28 octobre au soir, que la DILA a servi ; puis
  `textes.py --inscrire`, sept rédactions de deux décrets « à examiner »,
  poussées à part.
- **Le test d'abord.** `LUES_AU_DROIT` (`tests/test_carte.py`), la liste des
  fiches lues au droit, qui ne fait que grandir : rien ne leur manque, ce
  qu'elles disent d'elles-mêmes tient (`outils_carte`), et une rédaction que
  leurs versions citent n'est plus à rattacher ; vu rouge des deux fiches, de
  leurs six manques chacune. Et, dans `tests/test_rafp.py`, la période du
  régime de chaque année que couvre une version de l'assiette porte les taux que
  la version lit — la limite de 20 %, le taux de 10 %, sa moitié à l'agent — ;
  vu rouge faute de versions.
- **`rafp_assiette_plafond`**, du domaine des cotisations et de l'étape qui
  acquiert les droits, comme ses sœurs de la GIPA et du compte épargne-temps :
  quatre versions sur l'année du revenu. Rien avant 2005, l'article 76 n'entrant
  en vigueur qu'au 1er janvier. Puis la limite de 20 % du traitement indiciaire
  brut, le taux de 10 % et son partage, que ni les six rédactions de l'article 2
  du décret n° 2004-569, ni son article 3, ni les quatre de l'article 76 n'ont
  changés. La loi de finances pour 2023 retire de l'assiette, au 1er janvier
  2022, la participation de l'employeur à la protection sociale complémentaire
  et le remboursement forfaitaire de l'État (article 162, IV et V) ; la loi
  n° 2023-1268, au 1er septembre 2024, l'activité hospitalière des
  hospitalo-universitaires : deux versions de plus. Les conditions de chacune
  disent le reste : le détachement (article 4), l'activité privée, la solde
  des militaires nommée depuis 2019, le calcul cumulé de l'employeur mois par
  mois (arrêté du 26 novembre 2004, article 15, ses quatre rédactions), la
  priorité sur la cotisation volontaire d'outre-mer depuis avril 2024. Elle
  reste conforme : la saisie ne porte aucun des éléments que les textes
  retirent, ni le détachement, ce que son code dit ; l'ERAFP ne publie aucun
  exemple chiffré de la limite.
- **`rafp_beneficiaires`**, du domaine de la coordination et de l'étape des
  affiliations : deux versions, rien avant 2005, puis le II de l'article 76,
  inchangé d'un mot dans ses quatre rédactions. L'ERAFP, relu, écarte trois
  situations que le texte ne nomme pas : le statut local d'outre-mer, que le
  routage n'affilie pas au RAFP (`fonctionnaire_pacifique`) ; la disponibilité
  et la position hors cadre, sans rémunération de l'administration ; le
  titulaire employé moins de vingt-huit heures par semaine, que le statut ne
  distingue pas et que le routage porte au RAFP comme à la CNRACL. La fiche
  passe à `approchee`, de cette approximation, non mesurée, et demande sur
  quel texte l'ERAFP le fait, que l'index ne trouve pas.
- **Le cliquet des textes** descend de 9 504 à 9 494 : dix rédactions sans
  statut sont citées par une version — quatre de l'article 2 du décret, son
  article 3, les deux de son article 4, trois de l'article 76. L'inscription
  qui suit apporte la loi de finances pour 2023, que la fiche cite : 42
  rédactions « à examiner ».
- **La carte** passe de 106 fiches à lire au droit à 104, de 630 manques à
  618 ; elle compte une fiche conforme de moins, une approchée de plus.
  `conservation.py --depuis HEAD` dit changées les lignes de veille des deux
  fiches, refaites depuis elles, ce que la référence figée admet.

## Ce que l'étape laisse

- Les 104 fiches à lire au droit, par lots d'un régime ou d'un domaine, qui
  entrent à mesure dans `LUES_AU_DROIT`, et les points ouverts des phases 2
  à 8. Pour chaque lot, ce que celui-ci a appris : une version qui précède le
  régime naît de la loi qui le date, publiée avant le décret dont naît la
  suivante, sinon le partage trouve un trou à la date du décret ; une version
  nommée sur l'année du revenu peut commencer en cours d'année ; le cliquet
  s'abaisse dans `perimetre.yaml` d'autant de rédactions que les versions en
  citent pour la première fois.
- Lu en chemin, hors du lot : l'article 5 du décret, les points de l'année, n'a
  pas de fiche. L'ERAFP arrondit le nombre de points « au point supérieur »
  (350 € de cotisation en 2026, 240 points), ce que le modèle ne fait pas : au
  plus un point par an d'écart, à lire et à rejouer dans la fiche qui naîtra.
- `regenerer.py --verifier`, dans le clone, dit périmés le paquet, les
  témoins, le chiffrage, le tableau de bord et dix-sept chiffres ancrés de la
  prose : le tableau de bord compte la carte, le reste ne lit aucune des deux
  fiches. GitHub les refait.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
