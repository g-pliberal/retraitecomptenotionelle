# Correction de la ligne 22 de la file : la CARCDSF sert ses statuts de 2007 jusqu'au 30 juin 2011

Vingt-deuxième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Arrêté du 13 avril
2011 (JORFTEXT000023909782), publié le 27 : article 3 (JORFARTI000023909788), « Les
dispositions du présent arrêté entrent en vigueur à compter du 1er juillet 2011. » ;
article 2 (JORFARTI000023909786), « L'arrêté du 1er octobre 2007 portant approbation
des statuts du régime complémentaire d'assurance vieillesse de la caisse autonome de
retraite des chirurgiens-dentistes est abrogé. » Annexe (JORFARTI000023909792) : son
chapitre VI, « Dispositions transitoires », ne porte que sur les sages-femmes venues
de la CARSAF (articles 49 et 50) ; rien n'y touche la liquidation, et « 1er juillet
2011 » n'y figure pas. Le texte tranche ce que la ligne dit : une pension qui prend
effet de janvier à juin 2011 se liquide aux statuts de 2007, article 20
(JORFARTI000001859980), « 25 % pour un départ en retraite au cours de la 61e année »,
sans majoration après 65 ans.

**L'erreur.** La fiche du régime servait les statuts de 2011 à sa période de 2011,
l'année civile entière : les pensions du premier semestre recevaient la minoration au
trimestre depuis 65 ans, et la majoration de 1 % par trimestre au-delà, que les
statuts de 2007 ne servent pas.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_la_carcdsf_sert_ses_statuts_de_2007_jusqu_au_30_juin_2011`), vu rouge (le
coefficient 0,775 où le texte donne 0,75), puis vert ; quatre cas, servis par le
portage et refaits au bit près par le moteur Python (`servi_et_refait`). Dentiste au
double du salaire moyen depuis ses 20 ans, euros de 2026 ; les points ne dépendent pas
du texte qui liquide, et chaque attendu est la pension du taux plein multipliée à la
main :

- né le 1er septembre 1950, pension au 1er mars 2011, à 60 ans et 6 mois, « 61e
  année » : 8 507,7438 × 0,75 = **6 380,81 € par an, au lieu de 6 593,50 €**
  (212,69 € de trop) ;
- né le 1er octobre 1950, pension au 1er janvier 2011, à 60 ans et 3 mois :
  8 327,4606 × 0,75 = 6 245,60 €, au lieu de 6 349,69 € ;
- né le 1er janvier 1944, pension au 1er avril 2011, à 67 ans et 3 mois : aucune
  majoration, 9 410,90 €, au lieu de 10 257,88 € (846,98 € de trop) ;
- né le 1er janvier 1951, pension au 1er juillet 2011, à 60 ans et 6 mois, le jour
  des statuts de 2011 : le coefficient 0,775 que le modèle servait, inchangé
  (6 529,26 €).

`tests/test_coupures_au_mois.py` : la CARCDSF y était déjà, le commentaire nomme la
seconde coupure.

**La correction**, dans les données seules : `carcdsf_complementaire.yaml`, la période
de 2010 liquide jusqu'au 1er juillet 2011 (`date_effet: [2010-01-01, 2011-07-01]`),
celle de 2011 depuis ce jour (`date_effet: [2011-07-01, 2012-01-01]`). Les années
bornent toujours l'acquisition : 2011 se cotise au taux de 2011. Aucun code touché :
les deux moteurs lisent déjà `date_effet`, et le paquet du portage est refait.

**La fiche.** `carcdsf_minoration_age_seul` : l'écart sort des approximations et passe
à l'histoire de la fiche.

**La classe, pas le cas.** Les deux périodes de la caisse servies à l'année civile
contre leur texte, l'automne 2007 (ligne 21) et le premier semestre 2011, sont
corrigées ; reste celle du 1er au 9 janvier 2024 (ligne 26).

**Ce qui reste déclaré** : au 1er juillet 2011, « 5 % par année d'anticipation », que
le modèle compte au trimestre ; si les statuts de 2011 comptent l'exercice d'avant le
1er juillet 2011 pour la majoration ; la majoration au temps écoulé (ligne 24) ;
l'inapte et les catégories sans minoration (ligne 23) ; les sages-femmes de 2009 au
30 juin 2011, que les statuts de 2007 ne nomment pas ; l'article 18 du règlement de
1955, en vigueur jusqu'au 1er janvier 2011, non lu.
