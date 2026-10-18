# Étape 6, septième partie : l'outre-mer, le seuil d'un trimestre du département

**La demande.** Le lot 6 de la vague du 17-18 octobre 2026, où le propriétaire
demandait « toutes les tâches qui n'ont pas besoin de mes décisions » : le
premier point du bloc « Reprise » de l'étape, l'outre-mer, avec un champ de
saisie. Coupé au registre le 14 octobre, du rang « léger ou nul », le point a
été rouvert par la vague, comme la Lodeom le 17. Avant 1946, la retenue, et les
textes au fac-similé restent à d'autres sessions.

**Ce que disent les textes**, lus le jour même dans les index LEGI et JORF mis
à jour au 18 octobre (détail au journal de veille du jour).

- *R. 753-21* (LEGIARTI000006752616, de 1985 au 1er janvier 2026) : outre-mer,
  les cotisations comptent « depuis le 1er janvier 1948 » ; en 1948, autant de
  trimestres que le salaire représente de fois « 1.800 F métropolitains », ou
  « 900 F. C. F. A. » à La Réunion ; depuis 1949, de fois le trimestre de
  l'allocation aux vieux travailleurs salariés au 1er janvier « dans les
  départements mentionnés à l'article L. 751-1 ».
- *Le décret n° 2025-1409* (article 2, 44°) l'abroge, et *R. 351-39*
  (LEGIARTI000053327980) le garde pour les périodes d'avant 1952, comme les
  quatre premiers alinéas de l'ancien R. 351-9, chez qui avait plus de
  soixante-quinze ans en 2026 ou des périodes de plus de soixante ans : tous ceux
  qui ont de telles périodes.
- *R. 351-9*, toutes ses rédactions depuis 1985 : de 1972 à 2013, l'assuré qui a
  exercé son activité dans un département de L. 751-1 « au cours de tout ou
  partie d'une année » y prend le SMIC « en vigueur dans ledit département au
  1er janvier », sur 200 heures.
- *Le SMIC des départements d'outre-mer*, arrêté puis décrété à part jusqu'en
  1995 : la semaine de 40 heures à 220,74 F aux Antilles et en Guyane au
  1er décembre 1974 ; à 436,76 F, et 392,40 F à La Réunion, au 1er mars 1980 ;
  à 593,36 F et 553,64 F au 1er janvier 1982 ; la semaine de 39 heures à
  1 048,92 F et 1 012,07 F en 1991 (décret n° 90-1153), 1 094,37 F dans les
  quatre départements en 1992 (décret n° 92-17) ; 36,98 F de l'heure au
  1er janvier 1996, celui de la métropole (décret n° 95-1312).
- *D. 757-2* (1985-1991) : la condition d'ouverture de l'allocation aux vieux
  travailleurs salariés, une rémunération d'au moins l'allocation entière, puis
  800 heures de SMIC. C'est ce que porte le barème « AVTS - Validation des
  années de salariat » de la Cnav, sans effet sur le trimestre.

**Ce que la vérification a tranché.** Le barème « Salaire validant un
trimestre » de la Cnav redonne au centime 200 heures de chaque SMIC du Journal
officiel lu (la caisse tronque : 5 379,07 F pour 1 048,92 × 200 / 39). La
Réunion avait le SMIC le plus bas : c'est l'autre barème, celui de la condition
d'ouverture, qui intervertit les colonnes de 1975 à 1991. Les montants de
l'allocation des départements d'outre-mer de 1949 à 1951 — 15 000, 22 500 et
32 000 anciens francs au 1er janvier — ne s'écrivent qu'au barème : la loi
n° 50-147 (article 2) et les décrets n° 48-593, 50-1410 et 51-1441 n'ont dans
l'index que leur notice.

**Ce qui est fait.**

- *Les données* : `legislation/salaire_validant_trimestre_outre_mer.csv`, de 1948
  à 1995, une colonne pour la Guadeloupe, la Guyane et la Martinique, une pour
  La Réunion, au niveau `haute`, contrôlées par `verifier_donnees.py` (deux
  contrôles) ; le récupérateur (`cnav_avts.py`) refuse d'écrire si ses colonnes
  ne redonnent pas les SMIC du Journal officiel, ou si un seuil outre-mer
  paraît depuis 1996, et garde neuf décimales.
- *Le modèle* : `DonneesMacro.trimestres_valides(revenu, annee, outre_mer)` et
  `trimestresValides` : rien avant 1948 outre-mer, la table jusqu'en 1995, la
  métropole ensuite ; `DEPARTEMENTS_D_OUTRE_MER` dans les deux moteurs. Le
  paquet porte les deux séries et garde sa version : un paquet qui ne les a pas
  laisse l'outre-mer au seuil de la métropole.
- *La carrière* : `AnneeCarriere.outre_mer`, `LigneRelevee.outre_mer`,
  l'attribut `outre_mer` de la période d'activité de la chronologie ; le relevé,
  sa prolongation, le parcours et la carrière prolongée le portent. Depuis 1972,
  l'année d'un parcours prend le département dès qu'un métier de l'année y a
  été exercé (R. 351-9) ; avant, celui du métier qui en occupe le plus de mois,
  comme son statut. L'année validante du salaire annuel moyen lit le seuil du
  département (`Carriere.outre_mer`). Un département inconnu se refuse.
- *Le registre* : les deux points de `baremes_ipp` et d'OpenFisca-France-Pension
  passent de `coupe` à `repris` ; la fiche `trimestres_avant_1972` reste
  `approchee`, ses lectures et ses approximations récrites ; R. 351-39 y prend
  son statut, et le cliquet des textes descend d'un, à 9 678. `textes.py
  --inscrire` apporte 44 rédactions « à examiner » : R. 753-21 et D. 757-2, et
  39 que d'autres fiches citaient déjà (R. 613-17, le décret n° 84-936).
- *Les tests* : `test_outre_mer_le_trimestre_se_valide_au_seuil_du_departement`
  et son jumeau, les seuils posés depuis les textes ; `tests/test_outre_mer.py`,
  le département dans la carrière, et son jumeau ; deux contrôles du
  récupérateur (`tests/test_verification.py`).

**Ce que montrent les mesures.** Aucun témoin ne bouge : aucun n'a travaillé
outre-mer, et le site ne le demande pas encore. Une carrière de 1970 à 2012 à
12 % du salaire moyen valide de 1972 à 1995 73 trimestres à La Réunion, 69 en
Martinique et 49 en métropole ; à 8 %, 45, 45 et 25. Dès 20 %, rien ne change :
la métropole valide déjà les quatre trimestres de chaque année.

**Pour les pages, au propriétaire.** Rien n'éclaire encore la présentation : le
site ne demande nulle part où l'assuré a travaillé, et la seule famille
« Outre-mer » du menu des statuts sert aux collectivités qui ont leur régime.
Trois formes sont possibles. (a) Un bloc replié « Périodes outre-mer », comme
celui des périodes hors de France : le département, le mois où elle commence,
celui où elle finit ; la saisie couperait les métiers à ses bornes et poserait
l'attribut, et la Lodeom s'y logerait. (b) Une colonne « lieu » à chaque ligne
de la carrière. (c) Des statuts de la famille « Outre-mer » (« salarié de La
Réunion »…), qu'il faudrait doubler pour le cadre et le non-cadre. La forme (a)
pèse le moins sur le formulaire vierge, un titre replié, et c'est celle qu'on
recommande.

**Ce qui reste.**

1. *Au propriétaire* : la forme du champ ; puis le champ, dans les deux saisies,
   les deux contextes et les pages.
2. *Avant 1946*, la règle de la retenue (la session suivante).
3. *Au fac-similé* : les textes d'avant 1970, les plafonds de 1956 à 1981, les
   montants de l'allocation des départements d'outre-mer de 1949 à 1951.
4. *Le SMIC horaire du dépôt*, à six décimales d'euro, met le seuil de la
   métropole de 1996 à 1 127,513 € pour 7 396 F (1 127,51293 €) : un salaire pile
   sur ce seuil n'y valide pas. À la session des données.
