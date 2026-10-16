# Étape 2, quatrième famille : la carrière longue des fonctionnaires, confrontée à OpenFisca

**Le 16 octobre 2026, la demande.** La septième de quatorze sessions
parallèles, le propriétaire dormant : « action 153, étape 2, famille suivante.
La carrière longue de la fonction publique, confrontée à OpenFisca dans un
script et un test frères. Une erreur trouvée chez nous se corrige dans les
deux moteurs ; une erreur d'OpenFisca se consigne, le signalement attendant le
propriétaire. » Aucun fichier des pages ni de la saisie n'est touché, aucun
déplacé ; la liste des textes n'est pas inscrite (`textes.py --inscrire`, à la
session 8).

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part (avec un
`setuptools` d'avant 70) : `carriere_longue`,
`carriere_longue_seuil_determine_aod`, `duree_assurance_cotisee_seuil_bas` et
`_haut`, `ouverture_des_droits_carriere_longue_date`,
`ouverture_des_droits_date`, et les barèmes `carriere_longue/`, par génération
seulement. Dans l'index LEGI, à jour au 11 octobre : L. 25 bis du code des
pensions, rédactions de 2005, 2008 et 2010 ; l'article 57 de la loi
n° 2004-1370, pour la CNRACL ; D. 16-1, versions de 2011 et de 2012. Le journal
de veille a son entrée
(`2026-10-16-action-153-carriere-longue-fonction-publique.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_carriere_longue_fonction_publique.py` et portée par
le témoin (`tests/temoins/openfisca_carriere_longue_fonction_publique.json`) :

- *La carrière* : celle de la première famille, sédentaire, sans enfant.
- *L'entrée précoce* : la carrière commence l'année des quatorze à dix-huit
  ans, toute au régime de la liquidation. Ces années sont, dans la vie, celles
  d'un apprenti ou d'un auxiliaire ; OpenFisca ne lit l'entrée précoce que dans
  les services de la fonction publique.
- *Ce qui se compare* : le droit d'ouvrir la pension au 1er janvier de la
  liquidation — au dépôt, `liquidation_ouverte` et le motif ; chez OpenFisca,
  qui sert la pension même avant l'âge, sa date d'ouverture des droits au plus
  tard à la liquidation —, et la pension.
- *Rien n'est déclaré* : ni raison de départ, qui ouvrirait la carrière
  longue sans condition, ni catégorie.

**Ce qui est fait.** Douze profils, liquidés de 2004 à 2019 : quatre aux
portes d'avant 2009, deux entrés à dix-huit ans, deux à la CNRACL entrés plus
tôt, quatre à l'État sur la durée cotisée.
`tests/test_oracle_carriere_longue_fonction_publique.py`, au niveau des
contrôles : huit tests, la convention d'abord, une carrière à lacunes pour la
durée fixe, et le jumeau JavaScript sur les treize. Le manifeste a sa ligne
(`openfisca_carriere_longue_fonction_publique_oracle`) ; le registre deux
écarts, le point 153.2 et le bilan repris ; la fiche
`duree_requise_carriere_longue_fonction_publique` sa lecture du jour et son
bloc `referents` ; les limites un paragraphe.

**Ce que la confrontation a trouvé.**

- *Deux erreurs chez nous : les portes d'avant 2009.* L. 25 bis, dans sa
  rédaction du 1er janvier 2005, et l'article 57 de la loi n° 2004-1370 pour
  la CNRACL n'ouvrent la carrière longue aux fonctionnaires qu'« à compter du
  1er janvier 2005 », à cinquante-neuf ans, puis du 1er juillet 2006 à
  cinquante-huit, du 1er janvier 2008 à cinquante-six. Le dépôt leur ouvrait
  les trois portes du régime général dès 2004 : le fonctionnaire de l'État né
  en 1946, entré à quinze ans, partait à 58 ans en 2004 ; celui né en 1950, à
  57 ans en 2007. Et la durée y était fixe — 168 trimestres d'assurance, et
  168, 164 ou 160 cotisés selon la porte — jusqu'à la rédaction du
  19 décembre 2008, qui la rapporte à la durée de l'année des soixante ans ;
  le dépôt opposait celle de l'année d'ouverture, de 152 à 158 trimestres. Il
  ouvrait la porte de cinquante-neuf ans, en 2005, à 156 trimestres cotisés.
  Corrigé dans les deux moteurs : `CarriereLongue` porte les dates de chaque
  porte (`PORTES_FONCTION_PUBLIQUE_DEPUIS`) et la durée fixe
  (`DUREE_FIXE_FONCTION_PUBLIQUE`), opposées quand les régimes qui opposent la
  durée sont tous ceux de l'État et de la CNRACL. Aucun témoin de simulation
  ne bouge. OpenFisca, qui ne connaît la carrière longue que par génération,
  refuse ces départs : les deux concordent depuis.
- *Deux écarts chez OpenFisca* :

  | profil | le dépôt | OpenFisca | ce qui tranche |
  |---|---|---|---|
  | État, né en 1955, entré à 18 ans, parti à 60 ans en 2015 avec 168 trimestres cotisés | carrière longue, ouverte à 60 ans | aucune : l'entrée « avant vingt ans » lue à la fin de l'année des seize (`seuil_haut` recopie `seuil_bas`) ; droit à 62 ans | D. 16-1, I (décret n° 2012-847) |
  | les trois profils de la CNRACL | carrière longue | aucune : l'entrée précoce lue dans les services de l'État, écrits en dur dans le gabarit des régimes | loi n° 2004-1370, article 57 ; D. 16-1 |

  L'oracle a donc trouvé dix-huit erreurs chez OpenFisca, deux à cette
  famille, et trois chez nous.
- *Un défaut sans effet sur la pension.* OpenFisca date l'ouverture à l'âge
  de la porte, sur la durée cotisée à la liquidation : cinquante-six ans au
  fonctionnaire né en 1955 qui n'avait alors que 164 des 174 trimestres
  exigés. Le dépôt la date au mois où la durée est réunie, cinquante-huit ans
  et demi. Ces carrières ont toutes leur durée : la pension concorde au
  millionième sur les douze profils.

**Ce que le dépôt ne fait pas, vu en passant.** Le FSPOEIE garde les portes
du régime général dès 2004 : son texte (décret n° 2004-1056) n'a pas été lu.
La condition de durée d'assurance des portes d'avant le 1er novembre 2012,
168 trimestres, n'est opposée à personne, au régime général comme ailleurs,
la table ne portant que la durée cotisée : elle pèse sur qui part par la porte
de cinquante-neuf ans avec moins de 168 trimestres validés, non sur les
profils confrontés.

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux.

**Ce qui reste.** L'étape 2 continue, une famille par session : les minima,
les points enfants et la minoration de l'Arrco, les périodes assimilées, le
salaire annuel moyen sur des salaires qui varient. Le propriétaire tranche le
signalement à OpenFisca, de dix-huit erreurs désormais.
