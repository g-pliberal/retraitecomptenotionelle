# Étape 9, les règles : la partie III du jaune 2027 confrontée à la carte, une erreur du jaune tranchée, deux écarts du modèle déclarés

La partie III du jaune annexé au PLF 2027 (`data/brut/34465.pdf`, pages 87 à
143, tiré de la branche `jaune-2027`) a été lue en entier et confrontée, point
par point, aux fiches de la carte, sous la règle de `docs/veille_droit.md` : le
jaune est un exemple officiel, le texte tel que la caisse l'applique
l'emporte. Ce qui ne recoupait pas a été relu dans l'index LEGI du dépôt, mis à
jour au 13 octobre 2026. Les trois questions que l'étape 3 lui laissait sont
réglées : deux en écart déclaré, une en erreur du jaune.

## Ce qui recoupe

- **Le minimum garanti** (tableaux 43 à 46) : l'âge du minimum sans la durée,
  celui d'annulation de la décote minoré de neuf, sept, cinq, trois puis un
  trimestre pour un âge d'ouverture atteint de 2011 à 2015, ligne à ligne ; la
  référence de 1 366,35 € par mois au 1er janvier 2026, soit les 16 396,19 €
  par an de la fiche ; 785,65 € à quinze annuités ; le barème en escalier ; le
  quinzième de 57,5 % de l'invalidité ; l'écrêtement sans décret.
- **Les bonifications et majorations de durée** : le b ter de L. 12 (loi
  n° 2025-1403, article 104), un des deux trimestres de la majoration de L. 12
  bis compté en services ; la bonification du cinquième des militaires, à
  dix-sept ans de services ; le plafond de vingt trimestres des emplois classés
  depuis 2023 ; la majoration du dixième des hospitaliers actifs.
- **La majoration pour enfants**, son plafond au traitement ; **la majoration
  du handicap**, d'un tiers ; **l'invalidité**, sans décote, au minimum garanti
  sans condition, à 50 % du traitement à 60 % d'invalidité, avec sa rente
  viagère.
- **La réversion** : 50 %, sans condition d'âge ni de ressources, perdue au
  remariage ou au concubinage.
- **Les militaires** : la jouissance immédiate à dix-sept et vingt-sept ans ;
  la décote « carrière courte », dix trimestres au plus (`ouvrir.py`).
- **La carrière longue** : les réputés cotisés du tableau 39A, AVPF et aidants
  compris, et les deux trimestres d'enfants du décret n° 2026-700.
- **La surcote** : 1,25 % sans plafond depuis 2009, les seules bonifications
  d'enfants et de handicap comptées.
- **Le cumul emploi-retraite** : les règles communes aux pensions civiles
  liquidées depuis 2027, le régime propre des pensions militaires.

## Ce qui a changé dans la carte

- **`limite_age_fonction_publique`** : le tableau 57 donne soixante-quatre ans
  de limite d'âge aux techniciens supérieurs du développement durable affectés
  en mer ou au littoral et aux syndics des gens de mer. Le tableau des emplois
  classés annexé au code des pensions (rédaction du 25 mai 2024,
  LEGIARTI000049589035) leur donne soixante-deux ans, en toutes lettres : le
  jaune se trompe, la fiche le dit et garde soixante-deux.
- **`minimum_garanti`** : depuis le 1er septembre 2023, le dernier alinéa de
  L. 17 compte pour services effectifs, au minimum garanti, les périodes d'AVPF
  et d'aidant du fonctionnaire, dans la limite de vingt-quatre trimestres
  (R. 31-1, décret n° 2023-752). Le modèle ne les distingue pas : écart
  déclaré, dans la fiche et dans `docs/limites/ecarts-au-droit-positif.md`.
- **`surcote_parentale`** : le fonctionnaire a son texte, L. 14, IV, lu ; et
  L. 14, V, interdit de cumuler cette majoration avec la surcote ordinaire,
  quand le moteur ajoute l'une à l'autre. Le jaune ne tranche pas. Question
  ouverte dans la fiche, à lire chez le service des retraites de l'État et la
  CNRACL avant de toucher au moteur.
- **`cumul_emploi_retraite_et_retraite_progressive`** : le jaune donne le seuil
  du cumul de 2027, 7 000 € par an ; aucun décret ne le fixe dans les index de
  la DILA au 13 octobre 2026. Le paramètre reste non publié.

## Les contradictions du jaune, sans effet sur le dépôt

- La note 118 (page 117) reprend le texte de la note 120.
- La majoration pour tierce personne vaut « 13à9,99 € » au 1er avril 2026
  (page 128).
- Le tableau 56 porte sur les retraités « en 2016 », nés en 1954, en « €
  courant 2008 », source « EIR 2026 ».
- La décote « carrière courte » des militaires vise ceux mis à la retraite
  « avant l'âge de 52 ans » page 103, « avant l'AOD abaissé de 10 ans (soit
  54 ans à terme) » page 137.
- Le tableau 39B donne 166 trimestres au départ à 59 ans et 8 mois de la
  génération 1957, quand la ligne suit la durée de la génération plus quatre,
  170, comme pour 1956.
- La note 4 du tableau 57 fixe à soixante et soixante-cinq ans l'âge
  d'ouverture et la limite d'âge des paramédicaux passés en catégorie A, ceux
  de la loi de 2010, que les réformes de 2010 et 2023 ont relevés.
- La retraite anticipée du handicap cite la « loi n°270-2023 ».

## Ce qui reste

Trancher L. 14, V (fiche `surcote_parentale`) ; porter les périodes d'AVPF et
d'aidant du fonctionnaire quand la saisie les connaîtra ; guetter le décret du
seuil de L. 161-22, 2°. Les rachats, que le jaune décrit, restent
`pas_encore_modelisee`.
