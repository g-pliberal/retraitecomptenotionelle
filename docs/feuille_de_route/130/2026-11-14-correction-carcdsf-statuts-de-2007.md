# Correction de la ligne 21 de la file : la CARCDSF sert ses statuts de 2007 dès le 11 octobre 2007

Vingt et unième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Arrêté du 1er octobre
2007 (JORFTEXT000000252172), publié le 10 : article 1er (JORFARTI000001289079), « Sont
approuvés, tels qu'ils sont annexés au présent arrêté, les statuts du régime
complémentaire » ; article 2 (JORFARTI000002267801), l'arrêté du 6 janvier 1955 « est
abrogé à l'exception de l'article 18 » ; article 3, l'exécution. Aucun ne fixe de date.
Annexe (JORFARTI000001859980), article 20 : « b) Avec application d'un coefficient de
minoration, fonction de l'âge à la date à laquelle la pension prend effet pour les
assurés âgés entre 60 et 65 ans […] : - 25 % pour un départ en retraite au cours de la
61e année ; - 20 % […] de la 62e année ; - 15 % […] de la 63e année » ; les adhérentes
« à partir de 62 ans pour trois enfants » ; article 23, « majoré de 10 % au profit des
allocataires ayant eu au moins trois enfants ». Ni « transitoire » ni « 2008 » dans les
neuf pièces de l'arrêté. Le texte tranche ce que la ligne dit : en vigueur le 11
octobre 2007, lendemain de sa publication, il liquide les pensions qui prennent effet
le 1er novembre et le 1er décembre 2007.

**L'erreur.** La fiche du régime ne servait les statuts de 2007 qu'à sa période de
2008, « première année pleine » : les pensions de novembre et de décembre 2007 se
liquidaient par la période de 2004 à 2007, qui porte la décote du régime de base, que
la durée annule, sans la majoration pour trois enfants ni le taux plein avancé de la
mère.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_la_carcdsf_sert_ses_statuts_de_2007_des_le_11_octobre_2007`), vu rouge (le
coefficient 1 où le texte donne 0,85), puis vert ; cinq cas, servis par le portage et
refaits au bit près par le moteur Python (`servi_et_refait`). Dentiste au double du
salaire moyen depuis ses 20 ans, euros de 2026 ; les points ne dépendent pas du texte
qui liquide, et chaque attendu est la pension du taux plein multipliée à la main :

- né le 1er août 1945, pension au 1er novembre 2007, à 62 ans et 3 mois, « 63e
  année » : 7 529,1074 × 0,85 = **6 399,74 € par an, au lieu de 7 529,11 €**
  (1 129,37 € de trop) ;
- né le 1er septembre 1945, pension au 1er décembre 2007 : 7 543,3030 × 0,85 =
  6 411,81 € ;
- né le 1er août 1947, pension au 1er novembre 2007, à 60 ans et 3 mois, « 61e
  année » : 7 251,9622 × 0,75 = 5 438,97 €, au lieu de 7 251,96 € ;
- née le 1er août 1945, mère de trois enfants : sans minoration à 62 ans, 7 529,11 €,
  et 0,10 × 7 529,1074 = 752,91 € de majoration, au lieu de rien ;
- né le 1er juillet 1945, pension au 1er octobre 2007, dix jours avant les statuts :
  le coefficient 1 de la règle présumée, inchangé (7 514,91 €).

`tests/test_coupures_au_mois.py` : la CARCDSF entre dans la liste des régimes dont
une période se coupe au jour.

**La correction**, dans les données seules : `carcdsf_complementaire.yaml`, la période
de 2004 à 2007 liquide jusqu'au 11 octobre 2007 (`date_effet: [2004-01-01,
2007-10-11]`), celle de 2008 depuis ce jour (`date_effet: [2007-10-11, 2009-01-01]`).
Les années bornent toujours l'acquisition, dont le taux ne change pas en 2008. Aucun
code touché : les deux moteurs lisent déjà `date_effet`, et le paquet du portage est
refait.

**Les fiches.** `carcdsf_minoration_age_seul` : l'écart sort des approximations et
passe à l'histoire de la fiche ; `reversion_carcdsf` ne dit plus que la bonification
de l'affilié manque à l'automne 2007.

**La classe, pas le cas.** L'autre période de la caisse servie à l'année civile, le
premier semestre de 2011, est la ligne 22 de la file. La CAVAMAC est corrigée (ligne
10).

**Ce qui reste déclaré** : la règle d'avant le 11 octobre 2007, présumée (le règlement
de 1955 et ses modifications, au Bulletin officiel) ; l'article 18 de ce règlement,
resté en vigueur jusqu'en 2011, non lu ; les sages-femmes, que les statuts de 2007 ne
nomment pas ; l'inapte et les catégories sans minoration (ligne 23) ; les enfants
« élevés neuf ans », que le modèle compte comme les enfants déclarés ; l'entrée en
vigueur au lendemain de la publication, prise sans que l'article 1er du code civil
soit à l'index.
