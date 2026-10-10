# Étape 9, septième partie : l'histoire des prélèvements complétée — les indépendants, la maladie des pensions des autres régimes, l'ancrage au Journal officiel

**Reprise, au 10 octobre 2026.** Fait : les prélèvements hors retraite d'un
indépendant à leur année ; la maladie des pensions de la fonction publique,
des retraités indépendants et des salariés agricoles ; chaque marche de
`prelevements_historiques.yaml` ancrée au Journal officiel. Reste de l'histoire
des prélèvements, une session par point : la maladie des pensions des
exploitants d'avant 1997 et des régimes spéciaux ; la limite 5 ante ter (2),
à récrire à la fin de l'étape ; la complémentaire de la CNBF et celle de la
Cipav dans la fiche de paie, à la session des données ; les décrets qu'aucune
marche ne rejoint. Détail : plus bas, « Ce qui reste ».

**La demande.** Le propriétaire, le 10 octobre 2026, le point 5 de « Ce qui
reste » de la quatrième partie, dans l'ordre : les prélèvements hors retraite
des indépendants avant l'année courante, dont `revenus_nets` leur appliquait
les taux de 2026 (`FAMILLES`) ; la cotisation maladie des pensions des régimes
de base autres que le régime général, de 1980 à 1997, à chercher aux textes par
l'index de la DILA ; l'ancrage de chaque marche de l'IPP au Journal officiel,
sur le modèle de `ipp_taux_cotisation.py`. Il la nommait cinquième partie ;
l'écart au COR et l'âge d'équilibre ont pris la cinquième et la sixième le même
jour.

**Ce que disent les références, lues le jour même.**

- *Les barèmes de l'IPP*, en CSV et dans son dépôt YAML (commit `fe2cdff`) :
  la maladie des artisans et commerçants (`mmid_ac`) et des professions
  libérales (`mmid_pl`) depuis 1970, en tranches qui s'ajoutent (3,10 % sous
  le plafond et 8,45 % sous cinq plafonds font 11,55 % sous le plafond) ; la
  cotisation d'allocations familiales des indépendants depuis 1974, sa part
  plafonnée et sa part déplafonnée, puis ses taux modulés de 2015 et 2018 ; la
  maladie de leurs retraités (`assures_retraites`), que la quatrième partie
  croyait absente : elle est dans la branche des indépendants, non dans celle
  du régime général. Tout s'arrête en 2018.
- *L'index LEGI*, version par version : D. 612-4 de 1985 à 2017 — les taux
  des actifs et, au 2°, ceux des pensions —, D. 612-3 (la cotisation des
  retraités ne porte que sur leurs pensions de base, des caisses d'artisans,
  de commerçants, de libéraux et de la CNBF), D. 612-5 (la réduction de 2017
  sous 70 % du plafond, pour tous les indépendants non agricoles), D. 612-9
  (l'indemnité journalière, 0,50 % des artisans en 1995, des commerçants en
  2000, 0,70 % en 2007), D. 621-1 à D. 621-3 de 2018 à 2025, D. 613-1 ; L. 136-3
  depuis 1993 et l'article 129 de la loi de finances pour 1991 : « Les
  cotisations personnelles de sécurité sociale […] sont ajoutées au bénéfice
  pour le calcul de la contribution », jusqu'à l'assiette unique de 2025
  (loi n° 2023-1250, art. 18). Pour la fonction publique, D. 712-39, D. 713-16
  et l'article 3 du décret n° 67-850, que LEGI date de 1976 : 2,25 %, 2,65 % au
  1er juillet 1988, 3,05 % au 1er mars 1996, 2,80 % en 1997, « dans la limite
  du plafond » ; D. 711-3 à D. 711-5 pour les régimes spéciaux.
- *L'index JORF* : les décrets que l'IPP cite, et ceux qu'il ne cite pas. Le
  décret n° 91-745 vaut « pour les cotisations dues à l'échéance du
  1er octobre 1991 », le n° 92-295 porte 9,75 % à celle du 1er octobre 1992 ;
  le n° 95-556 fixe 0,25 % « pour l'année 1995 » seule ; le n° 84-817
  s'applique « à compter du 01-10-1984 », aux libéraux comme aux artisans ; le
  n° 87-483 porte la cotisation des retraités « de 3 % à 3,4 % ». Les salariés
  agricoles : 1 % et 2 % en 1980 (n° 80-481), 1,4 et 2,4 % en 1987 (n° 87-453,
  « du régime général de la sécurité sociale et du régime des assurances
  sociales agricoles »), 2,6 et 3,6 % en 1996 (n° 95-1401), 2,8 et 3,8 % en 1997
  (n° 96-1167, art. 7), 1 % sur la seule complémentaire en 1998 (n° 97-1252) :
  les taux du régime général. Les exploitants retraités : 2,8 % de part
  technique ramenés à 1,8 % en 1997, et 1 % de part complémentaire
  (n° 97-140) ; leurs taux d'avant tiennent à des décrets annuels dont l'index
  n'a que le titre.

**Ce qui est fait.**

- *Les indépendants* (`scripts/fetch/ipp_prelevements_sociaux.py`, partie
  `independants`) : la maladie des artisans et commerçants, 28 marches, celle
  des libéraux, 25, la cotisation familiale, 10, et l'assiette de la CSG, 2.
  L'IPP jusqu'en 2012 pour les premiers, 2016 pour les seconds, corrigé à
  quatre marches par les décrets (`CORRECTIONS`) ; puis les versions de LEGI
  (`LUES_AUX_TEXTES`), qui disent ce que l'IPP n'a pas ou a faux :
  l'indemnité journalière de 2013 à 2017, le déplafonnement de 2013 au
  1er janvier et non en mars, la réduction de 2017 des libéraux, 6,5 % sur
  tout le revenu au-delà de cinq plafonds en 2018 (l'IPP écrit 7,35 %), sur la
  seule fraction au-delà depuis le décret n° 2020-621, les barèmes de 2022 et
  de 2025. Un taux réduit s'écrit en paliers, interpolés sur tout le revenu
  comme `BaremeProgressif` le fait pour la fiche de paie.
- *Le lecteur* (`donnees/prelevements_historiques.py`) : les familles
  `artisan`, `commercant`, `liberal`, `avocat`, par les régimes de base de
  l'année (`famille_de_la_fiche`) ; la maladie et l'indemnité journalière, les
  allocations familiales, la CSG et la CRDS de l'activité sans abattement, sur
  le revenu augmenté jusqu'en 2024 des cotisations de l'année, retraite et
  invalidité-décès comprises. `revenus_nets` les prélève à l'année d'un
  indépendant ; l'invalidité-décès reste celle de l'année courante.
- *La maladie des pensions* : `maladie_fonction_publique`, lue aux textes, de
  1976 à 1997 ; `maladie_independants`, l'IPP sans son 3,1 % du 1er janvier
  1986, que D. 612-4 et le décret n° 87-483 démentent ; les salariés agricoles
  dans la série du régime général. `regimes_des_pensions` dit les régimes de
  chaque série, et `_parts_assujetties` leurs parts de la pension.
- *L'ancrage* : comme `ipp_taux_cotisation.py`, chaque texte que l'IPP cite
  est cherché dans l'index JORF, à son numéro — à son jour pour un arrêté — et
  à sa date de publication ; la marche porte ce qu'il trouve (`jorf`) ou ce
  qui manque (`ancrage`). 159 des 223 marches de l'IPP sont ancrées ; des 64
  autres, 22 n'ont pas de référence, 18 citent une convention, une circulaire
  ou un accord, 3 un article de code, 15 un texte que l'index n'a pas, et 6 un
  décret que l'index date autrement que l'IPP : les n° 93-93, 98-945,
  2002-1295, 2009-1158, 2012-853 (un an de trop) et 2014-1531. Les 24 marches
  lues aux textes sont liées au leur. La donnée tient sous 50 000 octets : les
  colonnes nulles des indépendants ne s'écrivent pas.
- *Les tests* (`tests/test_prelevements_historiques.py`, 7 cas de plus) :
  l'année courante d'un indépendant est sa fiche de paie, au centime, à neuf
  niveaux de revenu ; les marches corrigées et les barèmes des textes ; la CSG
  d'un indépendant sur ses cotisations jusqu'en 2024 ; le net d'un commerçant
  de 1985 ; la maladie des pensions des autres régimes, et celle d'une
  fonctionnaire partie en 1995 ; l'ancrage de chaque marche.

**Ce que montrent les mesures** (cas simples au salaire moyen, au scénario 1,
avant et après) :

- *Un indépendant* : son rendement interne ne bouge pas — son revenu net n'y
  entre pas —, mais tout ce qui se rapporte à son revenu net monte, quand il
  part avant 2025. Le commerçant de 1950, parti en 2014 : taux de
  remplacement net de 85,3 à 97,4 %, taux de remplacement sur le cycle de 0,770
  à 0,836 ; l'artisan de 1955 : de 98,4 à 104,5 % ; le libéral de 1960 : de
  48,5 à 50,7 %. Son dernier revenu payait une CSG sur ses cotisations, et
  5,4 % d'allocations familiales quand il en paie zéro sous 110 % du plafond
  aujourd'hui. Le commerçant de 1970, parti en 2034, ne bouge pas.
- *Un fonctionnaire de la catégorie active parti en 1995* : rendement interne
  réel net de 5,50 à 5,48 %, taux de remplacement net de 82,1 à 79,9 %. Le
  fonctionnaire parti en 1998 ne bouge pas.
- *La fiche de paie*, en chemin, et hors de cette partie : pour l'avocat de
  1975, la complémentaire de la CNBF prélève 59 % de son revenu en 2026 ; la
  Cipav n'apparaît sur celle du libéral qu'en 2023. Les deux étaient là avant ;
  aucun témoin ne les porte.

**Ce qui reste** de l'histoire des prélèvements, dans l'ordre :

1. *La maladie des pensions des exploitants agricoles d'avant 1997*, dans les
   décrets annuels de l'AMEXA, que l'index n'a qu'en titre : le dump de la DILA
   ou le recueil de la MSA. Sans fiche de paie, le dépôt ne calcule pas le net
   d'un exploitant : rien ne la lit encore.
2. *Celle des régimes spéciaux* (R. 711-8, puis D. 711-3 à D. 711-5 : 1,5 % en
   1985, 1,9 % en 1987, 2,85 % en 1996, 2,80 % en 1997 ; de 2,4 à 3,8 % sur les
   complémentaires que d'autres organismes leur servent), qui ne porte que sur
   les pensions des régimes placés sous le régime général pour la maladie : la
   liste est à lire, régime par régime.
3. *La limite 5 ante ter*, point 2, à récrire à la fin de l'étape : la fonction
   publique et les indépendants ne prélèvent plus rien sur une pension depuis
   1998, hors des non-résidents ; restent les régimes spéciaux.
4. *La fiche de paie de l'avocat et du libéral*, à la session des données : la
   complémentaire de la CNBF, la Cipav d'avant 2023, et l'indemnité
   journalière, que la fiche prête à tous au taux des artisans quand le libéral
   paie 0,30 % sous trois plafonds et l'avocat rien.
5. *Les décrets qu'aucune marche ne rejoint*, comme `ipp_taux_cotisation.py`
   les cherche pour la vieillesse ; et le plafond qui borne l'assiette de la
   maladie des pensions de la fonction publique, que le dépôt n'applique pas.
6. *Hors de cette partie*, inchangés : la prime spéciale de sujétion des
   aides-soignants, le taux de CSG d'une pension selon le revenu fiscal du
   foyer, l'indemnité compensatrice de la hausse de la CSG des agents publics
   et la cotisation de la RAFP, absentes de la fiche.
