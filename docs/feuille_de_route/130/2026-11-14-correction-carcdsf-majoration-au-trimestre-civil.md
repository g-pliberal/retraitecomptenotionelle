# Correction de la ligne 24 de la file : la CARCDSF majore par trimestre civil entier d'exercice libéral

Vingt-quatrième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026).

- Statuts de 2011, article 19, I, c (JORFARTI000023909792), en vigueur le 1er juillet
  2011 : « Les adhérents qui poursuivent leur activité libérale au-delà de l'âge prévu
  à l'article L. 161-17-2 du code de la sécurité sociale majoré de cinq ans, et qui
  n'ont pas fait liquider leurs droits à retraite dans le régime complémentaire,
  bénéficient d'une majoration de leur pension. Cette majoration est égale à 1 % par
  trimestre civil entier d'exercice libéral suivant le dernier jour du trimestre civil
  incluant l'âge mentionné à l'alinéa précédent, dans la limite de 20 %. »
- L'arrêté du 9 juillet 2012 (JORFARTI000026208364) n'y touche pas ; celui du
  22 décembre 2017 (JORFARTI000036251928), qui en fait l'article 35, n'y change que
  l'âge et ajoute « sous réserve de respecter les dispositions du deuxième alinéa de
  l'article 34 ».
- Statuts de 2024, article 35, I, c (JORFARTI000048880707), et règlement de 2026,
  article 3, I, c (JORFARTI000054435749) : les mêmes mots, 1 % pour le trimestre
  « accompli avant le 1er janvier 2024 », 1,25 % pour celui « accompli à compter du
  1er janvier 2024 ».

Le texte tranche ce que la ligne dit : le trimestre civil où tombe l'âge ne compte
pas, un trimestre entamé non plus, ni un trimestre sans exercice libéral.

**L'erreur.** Le modèle comptait le temps écoulé depuis l'âge du taux plein, le
quotient entier des mois par trois, que l'affilié exerce ou non : un trimestre de trop
quand l'âge tombe le premier mois d'un trimestre civil, ou selon le mois de l'effet ;
toute la majoration à qui avait cessé d'exercer.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_la_carcdsf_majore_par_trimestre_civil_entier_d_exercice_liberal`), vu rouge sur
cinq des six cas, puis vert ; servis par le portage et refaits au bit près par le
moteur Python (`servi_et_refait`). Dentiste au double du salaire moyen depuis ses
20 ans, euros de 2026 ; le décompte ne change pas les points, et chaque attendu est la
pension du taux plein multipliée à la main par la majoration du texte :

- né le 1er janvier 1948, 65 ans le 1er janvier 2013, pension au 1er janvier 2015 :
  sept trimestres civils entiers, d'avril 2013 à décembre 2014,
  10 339,4117 × 1,07 = **11 063,17 € par an, au lieu de 11 166,56 €** (103,39 € de
  trop) ;
- le même, sans activité de 2010 à 2014 : aucun trimestre d'exercice, **8 562,88 € au
  lieu de 9 247,91 €** (685,03 € de trop) ;
- le même, qui cesse le 31 décembre 2013 : trois trimestres, 9 981,0188 × 1,03 =
  10 280,45 € au lieu de 10 779,50 € ;
- né le 1er janvier 1953, taux plein le 1er mars 2019, pension au 1er mars 2022 : onze
  trimestres, d'avril 2019 à décembre 2021, 13 865,6396 × 1,11 = 15 390,86 € au lieu de
  15 529,52 € ; au 1er janvier 2022, les mêmes onze, 15 158,93 €, inchangé ;
- né le 1er janvier 1958, pension au 1er janvier 2028 : onze trimestres à 1,25 %,
  17 610,7061 × 1,1375 = 20 032,18 € au lieu de 20 252,31 €.

Le test ancien `test_la_carcdsf_majore_apres_son_age` tenait deux valeurs rendues par
le modèle (1,10 et 1,08) : il tient celles du texte, 1,0875 et 1,07.

**La correction.** Un interrupteur neuf, `surcote_trimestres_civils_d_exercice`
(`regimes/_schema.yaml`, `PeriodeRegime`, le paquet par `_regles_des_sections`), que
la fiche `carcdsf_minoration_age_seul` déclare et auquel renvoient les quinze périodes
de `carcdsf_complementaire.yaml` depuis le 1er juillet 2011. Sous lui, `surcotePoints`
(`moteur/js/droit/liquider.js`) et son jumeau ne lisent plus le temps écoulé : le
décompte part du trimestre civil qui suit celui de l'anniversaire
(`moisDeLAnniversaire`), s'arrête à la date d'effet, et `trimestresCivilsDExercice`
n'y retient que les trimestres civils dont une ligne cotisée au régime couvre les
trois mois. Le code du régime liquidé descend pour cela d'`abattementPoints` à
`surcotePoints`, en dernier argument. La limite de vingt trimestres s'applique ensuite,
inchangée.

Aucun témoin de simulation ne bouge.

**La fiche.** `carcdsf_minoration_age_seul` : l'interrupteur ; l'écart sort des
approximations, où ne reste que ce qui suit, et passe à l'histoire ; l'écart voisin,
celui de la ligne 25, dit ce que la correction lui retire. La fiche commune
`surcote_par_age_seul` perd la question qu'elle renvoyait ici.

**Ce qui reste déclaré.**

- L'exercice n'est connu qu'à l'année de la carrière, ses mois seulement l'année de
  l'entrée et celle du départ : une cessation en cours d'année ne se déclare pas.
  L'exercice libéral est lu comme une ligne cotisée au régime, ce qu'aucun texte lu ne
  définit.
- « Sous réserve de respecter les dispositions du deuxième alinéa de l'article 34 »
  (l'article 2 du règlement de 2026), d'être à jour de ses cotisations : le modèle ne
  le connaît pas.
- Les trimestres d'exercice d'avant le 1er juillet 2011 comptent au modèle ; le texte
  ne le tranche pas.
- Le taux de 1,25 % servi aux trimestres d'avant 2024 et l'âge de départ des nés de
  1951 à 1954 : la ligne 25. Né le 1er janvier 1955, pension au 1er janvier 2025 : le
  modèle rend désormais 1,1375, le texte 1,12.

**La classe, pas le cas.** La même erreur à la CARMF et à l'ASV est la ligne 18 de la
file ; à la CARPIMKO, le trimestre civil qui commence le jour de l'âge est un point
que le texte ne tranche pas (`surcote_par_age_seul`). L'interrupteur neuf y servirait
pour le décompte, non pour l'exercice, que ces textes ne demandent pas.

**Fichiers fabriqués refaits ici** : le paquet (`construire_donnees.py`) ; les témoins
(`construire_temoins.py`), inchangés.

**Vérifié** : `python -m pytest -m rapide` ; `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_carte.py`,
`test_donnees.py`, `test_coupures_au_mois.py`, `test_facade.py`,
`test_facade_jumeau.py`, `test_versions.py`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts.
