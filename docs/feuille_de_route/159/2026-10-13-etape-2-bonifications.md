# Étape 2, les bonifications : l'édition 2027 lue, certifiée, et les cinq fiches à jour

`bonifications_jaune.csv` porte désormais le jaune annexé au PLF 2027 : le
stock de pensions en paiement en 2025 (tableau A-7), le flux de 2025
(tableaux 50 et B-1), 143 valeurs certifiées, autant qu'avant. Les cinq fiches
d'`avantages_non_contributifs.yaml` qui citent le jaune — le cinquième des
militaires et des services actifs, le dépaysement, les bénéfices de campagne,
les services aériens et sous-marins — citent les chiffres de 2025, et
`--confronter` retrouve les trente-neuf dans le document.

**Le lecteur.** Les trois lecteurs de `scripts/fetch/sre_jaune_pensions.py`
échouaient sur l'édition 2027, dont les tableaux gardent les numéros mais non
la mise en page. Trois raisons :

- ses cellules sont centrées dans leur case, à des hauteurs qui varient d'un
  demi-point, et le lecteur PDF, qui range l'ordonnée avant l'abscisse,
  rendait la ligne des civils du tableau 50 dans le désordre. Il apprend une
  option, `par_abscisse` (`lecture_pdf.lignes_par_page`), qui relit chaque
  ligne de gauche à droite ; sans elle, rien ne change pour les autres
  lecteurs ;
- l'insécable des milliers y est posée à part, et le lecteur l'entourait de
  deux espaces : « 1 343 118 » faisait trois cellules. `_recoller` la rend à
  ses chiffres ;
- le tableau 50 est coupé entre deux pages : sa lecture passe à la suivante,
  jusqu'à la ligne « Sources », et reconnaît la population où qu'elle soit
  dans la ligne (« Gain en FPE Civils … »).

Le script lit les deux éditions (`--edition 2026` ou `2027`, la seconde par
défaut), chacune sous son jeu du manifeste et dans son fichier de
`data/brut/`. L'édition 2026, relue par l'ancien code et par le nouveau, rend
des tableaux identiques.

**Une case fausse dans le document.** Le tableau 50 donne 4,0 % des civils de
l'État liquidants à la bonification pour enfant, quand son ensemble est à
56,7 % et que la somme de toutes les parts ne fait que 22,0 %. Le tableau B-22
du même jaune tranche : 20 736 bénéficiaires sur 47 104 pensions civiles
entrées en paiement en 2025, 44,0 % — un chiffre manque à la case. Le B-22
établit aussi l'année du tableau 50, que son encart ne dit pas : chacune des
autres parts des civils s'y retrouve (dépaysement 4 079, soit 8,7 % ;
campagne 442, 0,9 % ; hors L. 12 3 631, 7,7 %). La valeur reste dans le
fichier telle que le document l'imprime ; le lecteur la signale
(`incoherences_50`, et le champ `incoherences` du fichier lu), l'en-tête du
CSV le dit, et aucune fiche ne la cite.

**La certification.** `scripts/verifier_donnees.py` lit l'édition 2027 et
écrit l'en-tête qui la date. Le fichier a été refait de zéro, sans quoi les
trois lignes de B-1 de 2026, dont la clé change avec l'accent que
l'édition 2027 rend (`ensemble_des_departs`), seraient restées.

**Le manifeste.** `sre_jaune_pensions_2027` passe à `certifie`, avec ses deux
cibles ; `sre_jaune_pensions`, l'édition 2026, à `saisi` : elle reste la
source des valeurs saisies de 2024 et 2023, le militaire moyen des cas types,
les cotisants de l'État et des référents, que les étapes 4 à 6 feront passer
à 2027. Le test qui recoupe la majoration pour enfants avec le jaune
(`test_avantages.py`) garde ses chiffres de 2024 : il le dit, et l'étape 6 le
refera.

**Ce qui reste**, pour les étapes suivantes : les autres tableaux du jaune,
selon l'inventaire de l'étape 0.
