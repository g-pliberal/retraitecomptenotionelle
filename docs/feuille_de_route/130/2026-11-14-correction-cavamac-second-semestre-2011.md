# Correction de la ligne 10 de la file : la CAVAMAC sert ses statuts de 2011 dès le 1er juillet 2011

Dixième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Arrêté du 23 juin 2011,
publié le 29 : article 2 (JORFARTI000024270156), « Les dispositions du présent arrêté
entrent en vigueur le 1er juillet 2011. » ; article 3 (JORFARTI000024270158), l'arrêté
du 22 décembre 1967 modifié « est abrogé » ; annexe (JORFARTI000024270173), article 16,
« Une majoration de 5 % du nombre de points de retraite acquis au compte de l'adhérent
est appliquée pour chaque année pleine différée au-delà de l'âge mentionné à
l'article 15 des présents statuts, dans la limite maximum de 25 %. » ; article 17, les
majorations des articles 18 et 19 « sont calculées sur la base du compte de droits
majoré ou minoré de l'adhérent » ; article 18, « Le nombre des points de retraite acquis
dans le présent régime est majoré de 10 % au profit de l'adhérent ayant eu au moins
trois enfants ». Ni « 2011 », ni « 2012 », ni « transitoire » dans les 29 983 caractères
de l'annexe. Le texte tranche ce que la ligne dit : une pension qui prend effet du
1er juillet au 1er décembre 2011 se liquide aux statuts de 2011.

**L'erreur, une seule cause, deux effets.** La fiche du régime ne servait les statuts de
2011 qu'à sa période de 2012, « première année pleine » : les pensions du second semestre
de 2011 se liquidaient par la période de 2004 à 2011, qui ne porte ni la majoration pour
trois enfants (fiche `sections_liberales_majoration_enfants`, 1 332,33 € au cas posé, ce
que la ligne chiffre), ni la majoration pour année différée (fiche
`cavamac_minoration_age_seul`, qui déclarait le même semestre). La correction de l'une
est celle de l'autre : les deux écarts sortent des approximations et passent à
l'histoire de leur fiche.

**Le test d'abord** (`tests/test_sections_liberales.py`), vu rouge (0 € servi où le
texte donne 1 332,33 € ; le coefficient 1 où le texte donne 1,05), puis vert :

- `test_la_majoration_pour_enfants_des_sections_aux_dates_qui_comptent_dans_les_deux_moteurs` :
  le cas du 1er juillet 2011 attend 10 %, et, posé à la main, 13 323,31 € de pension et
  1 332,33 € de majoration, servis par le portage et refaits au bit près par le moteur
  Python (`servi_et_refait`) ;
- `test_chaque_version_de_la_majoration_pour_enfants_des_sections_est_portee` : plus
  aucune date d'effet omise, 1 836 dates vues ;
- `test_les_lectures_de_la_majoration_pour_enfants_des_sections_que_le_modele_ne_suit_pas_sont_declarees` :
  deux écarts déclarés au lieu de trois ;
- `test_la_cavamac_majore_l_annee_differee_des_le_1er_juillet_2011`, neuf : l'agent né
  le 1er février 1945, 1,05 en novembre et en juillet 2011, 1 en juin ;
- `tests/test_coupures_au_mois.py` : la CAVAMAC entre dans la liste des régimes dont une
  période se coupe au jour.

**L'effet au cas posé** : née le 10 mars 1946, mère de trois enfants, agent général au
double du salaire moyen depuis ses 22 ans, pension à 65 ans et 3 mois (1er juillet
2011), euros de 2026. Le taux plein est à 65 ans, aucune année pleine n'est différée :
la pension de la CAVAMAC reste 13 323,31 € ; article 18, 0,10 × 13 323,31 = 1 332,331,
**1 332,33 € par an** de majoration, au lieu de rien. Pour l'année différée : l'agent
né en février 1945, parti en novembre 2011 à 66 ans et 9 mois, reçoit ses points
majorés de 5 % (7 774,42 € au lieu de 7 404,21 €) ; né en février 1940, à 71 ans et
9 mois, de 25 %, le plafond.

**La correction**, dans les données seules : `cavamac_complementaire.yaml`, la période
de 2004 à 2011 liquide jusqu'au 1er juillet 2011 (`date_effet: [2004-01-01,
2011-07-01]`), celle de 2012 à 2018 depuis ce jour (`date_effet: [2011-07-01,
2019-01-01]`). Les années bornent toujours l'acquisition, dont le taux ne change pas
en 2012. Aucun code touché : les deux moteurs lisent déjà `date_effet`, et le paquet
du portage est refait.

**La classe, pas le cas.** Les autres statuts servis à l'année pleine suivante sont
déjà dans la file : la CARCDSF en 2007 et en 2011 (lignes 21 et 22). Les six régimes
déjà coupés au jour ne sont pas touchés.

**Ce qui reste déclaré** : les statuts d'avant le 1er juillet 2011, non lus (le modèle
y présume la minoration de 2011 et n'y sert aucune majoration) ; les 5 % par enfant
handicapé de l'article 19 ; les enfants élevés neuf ans ; les lignes 27 à 30 de la
file, sur la même caisse.
