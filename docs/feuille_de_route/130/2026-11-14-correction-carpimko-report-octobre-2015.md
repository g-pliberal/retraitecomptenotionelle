# Correction de la ligne 16 de la file : la CARPIMKO majore le report dès le 3 octobre 2015

Seizième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Arrêté du 31 juillet
2015 (JORFTEXT000031255542), publié au Journal officiel du 2 octobre 2015. Article 1er
(JORFARTI000031255544) : « Sont approuvées, telles qu'elles sont annexées au présent
arrêté, les modifications apportées aux statuts de la section professionnelle des
auxiliaires médicaux. » L'article 2 charge le directeur de la sécurité sociale de
l'exécution. Annexe (JORFARTI000031255547), 4°, article 12 ter : « Lorsque la
liquidation de la retraite est ajournée au-delà de l'âge auquel elle aurait pu être
liquidée sans abattement, les assurés peuvent bénéficier d'une majoration de leur
pension. Cette majoration est égale à 1,25 % par trimestre civil entier d'ajournement
postérieur à l'âge du taux plein dans la limite de vingt trimestres. » Ni « vigueur »,
ni « compter du », ni « 2016 », ni « transitoire » dans l'annexe : l'arrêté entre en
vigueur le lendemain de sa publication, le 3 octobre 2015. Le texte tranche ce que la
ligne dit : une pension qui prend effet depuis ce jour est majorée.

**L'erreur, une seule cause, deux effets.** La fiche du régime ne servait l'arrêté
qu'à sa période de 2016, « première année pleine » : les pensions du 1er novembre et
du 1er décembre 2015 se liquidaient par la période de 2015, qui ne porte ni la
majoration de l'article 12 ter (ce que la ligne chiffre), ni les âges de l'article
12 quater (la table `carpimko_2016`, écart que la fiche `carpimko_ages_2015`
déclarait pour les mêmes trois mois). La correction de l'une est celle de l'autre.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_carpimko_majore_le_report_des_le_3_octobre_2015_dans_les_deux_moteurs`), vu
rouge (aucun coefficient au 1er novembre 2015 où le texte donne 1,075), puis vert. Né
le 10 mars 1949, auxiliaire médical au double du salaire moyen depuis ses 25 ans : 160
trimestres à 65 ans, quand sa génération en doit 161 ; le taux plein lui vient de
l'âge seul, 65 ans (article 12 quater, 1°), le 10 mars 2014.

| pension au | trimestres civils entiers d'ajournement | servi avant | servi depuis |
|---|---|---|---|
| 1er octobre 2015 | l'arrêté n'est pas en vigueur | sans majoration | sans majoration |
| 1er novembre 2015 | six, d'avril 2014 à septembre 2015 : 1,075 | 5 298,19 € | 5 695,55 € |
| 1er décembre 2015 | six : 1,075 | sans majoration | 1,0750 |

L'effet au cas posé : 5 298,1861 × 0,075 = 397,36 € par an de plus, ce que la ligne
annonçait « au moins ». Le cas de la note d'E14, entré à 22 ans, dont la durée est
atteinte à 62 ans et 3 mois : dix-sept trimestres, 1,2125, 6 424,05 € au lieu de
5 298,19 €, 1 125,86 € de plus. Le test passe par `servi_et_refait` : le moteur Python
refait chaque cas au bit près. `tests/test_coupures_au_mois.py` : la CARPIMKO entre
dans la liste des régimes dont une période se coupe au jour.

**Le code : aucun.** `carpimko_complementaire.yaml` : la période de 2015 liquide
jusqu'au 2 octobre 2015 (`date_effet: [2015-01-01, 2015-10-03]`), celle de 2016 depuis
le 3 (`date_effet: [2015-10-03, 2017-01-01]`). Les années bornent toujours
l'acquisition. Les deux moteurs lisent déjà `date_effet` au paquet.

**Ce que la correction déplace.** Aucun des 933 témoins de simulation ; un rendu de
page, `methode`. Fabriqués refaits, que les tests lisent : le paquet, les témoins, et
la page `methode/index.html` (`construire_pages.py`), que la suite rapide réclamait.

**Les fiches.** `surcote_par_age_seul` : l'erreur passe à l'histoire (`effet`), et son
approximation devient la réserve de la date d'effet. `carpimko_ages_2015` : l'écart des
trois mois sort des approximations et passe à l'histoire (`effet`).
`liquidation_regime_par_regime` : la CARPIMKO n'est plus servie à l'âge de la base
qu'avant le 3 octobre 2015. Les limites ne nommaient pas l'année 2016 : rien à y
récrire.

**La classe, pas le cas.** « Première année pleine » ne se lit plus dans aucune fiche
de régime : la CAVAMAC et la CARCDSF ont été coupées au jour aux lignes 10, 21 et 22.

**Ce qui reste déclaré.** La date d'effet de 1987 à juillet 2026, dont l'article n'est
pas lu : si la pension ne prend effet qu'au premier jour d'un trimestre civil, aucune
ne prend effet du 3 octobre au 31 décembre 2015, et la correction ne sert personne.
Le trimestre civil qui commence le jour où l'âge, ou la durée, est atteint, que le
texte ne tranche pas. Les 4 % par année d'anticipation des générations 1955 et
antérieures, que la période de 2016 ne porte pas et qu'elle étend à ces trois mois :
la ligne 19 de la file. Le bloc « Reprise » de l'action 130 n'est pas récrit : la file
dit où elle en est.
