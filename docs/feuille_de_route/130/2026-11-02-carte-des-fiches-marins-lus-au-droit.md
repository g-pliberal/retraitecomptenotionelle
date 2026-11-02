# La carte des fiches : les marins lus au droit, cinquième lot

**La demande.** Le 2 novembre 2026, la session d'orchestration confie à la
file E un nouveau lot de la carte (action 130), hors des régimes des autres
files et de ceux déjà lus — le RAFP, la CNAVPL, les IEG, la SNCF et la RATP
(`130/2026-11-02-carte-des-fiches-sncf-et-ratp-lues-au-droit.md`). Le lot
pris : le régime des marins (ENIM), dont les trois fiches n'étaient pas
mûres : `marins_ouverture_cinquante_ans`, `marins_bonification_enfants` et
`marins_salaire_de_reference`. Aucun chiffre du modèle ne bouge. En même
temps, la file G corrige la durée de la CRPCEN et de la Comédie-Française,
sous le même numéro, dans sa propre note.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF
  récupérés, à jour de l'incrément du 2 novembre ; `textes.py --inscrire`,
  quatorze rédactions nouvelles « à examiner », toutes de textes que d'autres
  fiches citent, aucune des marins.
- **Le test d'abord.** Les trois fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs dix-neuf manques ; un fichier
  neuf, `tests/test_marins.py`, vu rouge faute de versions. Chaque paramètre
  d'une version y porte le nom du champ de la période qui le porterait :
  `regimes/marins.yaml`, une seule période depuis 1930, en porte la valeur, ou
  la fiche déclare l'écart, et vingt-deux cas le tiennent, chacun par
  l'article qu'en cite l'approximation. Un test mesure, sur les données du
  dépôt, ce que l'abattement de R. 11, 3° ferait en 2026. Une valeur altérée
  dans chaque fiche le fait rougir.
- **Les rédactions, article par article**, chacune contre la suivante : au
  code des pensions de retraite des marins, R. 2, R. 3, R. 5, R. 11 à R. 14,
  R. 30, R. 31, L. 4, L. 5, L. 7, L. 8, L. 14, L. 15, L. 17 et L. 42 ; au code
  des transports, qui reprend sa partie législative le 1er décembre 2010,
  L. 5552-4, L. 5552-5, L. 5552-12, L. 5552-19, L. 5552-22 et L. 5553-5 ; au
  Journal officiel, les analyses des décrets n° 68-292 (le code, qui abroge la
  loi du 12 avril 1941), n° 79-791 (R. 14) et n° 85-1159 (R. 13), et le décret
  n° 99-265 (R. 31). Ni la loi de 1941 ni la rédaction de 1968 de R. 14 ne sont
  dans un index : leurs versions sont supposées. Aucun relèvement des âges des
  marins au Journal officiel depuis 2010.
- **L'ENIM** : ses pages publiques renvoient le 2 novembre au portail des
  assurés ; la lecture du 22 septembre reste la dernière.
- **`marins_ouverture_cinquante_ans`**, du domaine de l'âge et de l'étape qui
  ouvre le droit : trois versions sur la date d'effet — la loi de 1941,
  présumée codifiée à droit constant ; le code de 1968, cinquante ans et
  vingt-cinq ans de services, vingt-cinq annuités au plus avant cinquante-cinq
  ans ; depuis le 7 novembre 1985, ce plafond levé pour le marin de
  cinquante-deux ans et demi qui réunit trente-sept annuités et demie.
  Approchée, de conforme : le modèle sert la levée dès 1930.
- **`marins_bonification_enfants`**, du domaine des enfants et de l'étape qui
  complète : trois versions — la loi de 1941 et le code de 1968, présumés aux
  taux de 1979 (L. 17 bonifie dès deux enfants « élevés jusqu'à un âge
  déterminé ») ; depuis le 15 septembre 1979, 5 %, 10 % et 15 % pour l'enfant
  élevé neuf ans avant ses seize ans. Approchée, de conforme : la condition
  d'éducation n'est pas opposée, même à l'enfant de moins de neuf ans.
- **`marins_salaire_de_reference`**, du domaine du salaire de référence et de
  l'étape qui liquide : trois versions — la loi de 1941, présumée ; le code de
  1968, R. 11 et R. 12 ; depuis le 9 avril 1999, R. 31 pour les contrats à
  temps partiel simultanés. Elle reste approchée, et l'est davantage.
- **Le cliquet des textes** descend de 9 435 à 9 423. **La carte** passe de 95
  fiches à lire au droit à 92, de 569 manques à 550. `conservation.py --depuis
  HEAD` dit changées les lignes de veille des trois fiches, refaites depuis
  elles, ce que la référence figée admet.

## Ce que l'étape laisse

- **Une erreur du modèle, pour une étape du modèle** (la file E ne touche pas
  au modèle) : le 3° de R. 11, inchangé depuis 1968, que L. 5552-19 reprend en
  2010 (« sous réserve d'un abattement au-delà d'un plafond ») : « Lorsque le
  salaire ainsi défini excède huit fois le montant du traitement brut
  correspondant à l'indice 100 dans la fonction publique, la portion dépassant
  cette limite n'est comptée que pour moitié. » Le modèle liquide le forfait
  entier. Lu à l'indice 100 majoré — 5 907,34 € par an depuis le 1er juillet
  2023 —, le plafond vaut 47 258,72 € en 2026 : les catégories 15 à 20 le
  dépassent, et leur salaire de référence est surestimé de 2,1 % à 19,3 % ;
  depuis 2008, les catégories 17 à 20, 16 à 20 dès 2013, 15 à 20 dès 2024. La
  correction est une donnée et une règle, dans les deux moteurs : le plafond
  lu dans `legislation/point_indice_fonction_publique.csv`, appliqué au
  forfait de la catégorie ; `test_ce_que_le_modele_fait_autrement_la_fiche_le_declare`
  rougira alors, et la fiche perdra son approximation. À faire confirmer
  d'abord par l'ENIM, qui ne l'écrit pas sur ses pages : comment elle lit
  « l'indice 100 ».
- **Deux écarts plus petits, déclarés** : la levée des cinquante-deux ans et
  demi servie aux pensions d'avant le 7 novembre 1985, qu'aucun témoin ne
  porte ; la bonification servie pour un enfant de moins de neuf ans à la date
  d'effet (5 % de trop par enfant). Le second se corrigerait par la présomption
  `enfant_eleve_neuf_ans`, que les fiches de la majoration de durée appliquent
  déjà.
- **Sans fiche** : les âges de la pension proportionnelle (R. 3, L. 5) et de la
  pension spéciale (R. 5, L. 7, L. 8, L. 5552-12), que le modèle sert, restent
  sans statut dans la liste des textes ; avant le 28 janvier 1987, la pension
  spéciale sans autre pension renvoyait à l'âge de l'ancien L. 345 du code de
  la sécurité sociale, qu'aucun index ne porte. La formule des marins, 2 % du
  forfait par annuité, et son maximum de quarante annuités avec les
  bonifications de R. 6, que le modèle ne sert pas.
- Les 92 fiches à lire au droit. Ce que ce lot ajoute : un article qui ne
  change pas peut porter une règle que personne n'a lue — le 3° de R. 11 était
  dans la rédaction lue le 22 septembre ; un décret de codification n'a, au
  Journal officiel de l'index, que son analyse.
- `regenerer.py --verifier` dirait périmé le tableau de bord, qui compte la
  carte ; GitHub le refait.

## Ce qui attend le propriétaire

Une question : ouvrir une étape du modèle pour l'abattement du salaire de
référence des marins au-delà de huit fois l'indice 100, après en avoir fait
confirmer la lecture par l'ENIM ? Pour le reste, rien de neuf : la septième
étape du sixième domaine, la décision de la proposition, et celle sur la
retraite progressive, le cumul et la seconde pension, README muet.
