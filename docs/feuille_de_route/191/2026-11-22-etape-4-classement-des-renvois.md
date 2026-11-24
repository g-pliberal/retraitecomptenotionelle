# Étape 4 de la note 0009, deuxième session : les renvois sans texte, classés par leur poids

**Reprise, au 24 novembre 2026.** L'étape 7 de la note 0009 mène les lots
de cette note. Il reste 277 renvois d'un régime à une fiche sans texte
cité. Le budget du propriétaire du 22 novembre tient : d'abord les
renvois qui ne changent aucun cas mesuré, qu'il suffit de citer ; puis les
trente plus lourds, par lots de six, chacun lu au texte et relu par une
autre session, et trois à cinq règles contrôlées en Catala hors du dépôt.
Après les trente, point d'arrêt : le compte au propriétaire, qui décide des
autres. Le premier lot du rangement en a cité neuf et en a relevé
neuf, dont la ligne ne s'ouvre pas au jour du texte
(`2026-11-24-etape-7-rangement-premier-lot.md`). Continuer par la réforme
des régimes spéciaux de 2008. Les frontières dont l'étape 6 n'a pas lu le
texte se datent ici, avec les renvois de leur régime.

Le 22 novembre 2026, la nuit, sur Opus 5.5. Aucun fichier du dépôt n'est
touché hors cette note : la mesure tourne hors du dépôt, sur le paquet du
jour, et ses scripts (`poids3.py`, `classer3.py`) et son tableau complet
(`classement.csv`) sont rangés dans les fichiers du projet
(`architecture/191-etape-4b-classement/`). Deux relectures sur Opus, par
une autre session, ont fait reprendre la mesure (plus bas).

**Ce qui est compté.** Les séries que `tests/outils_droit_date.py` appelle
renvois, et dont la période d'ouverture ne cite rien
(`texte_cite(serie) is None`) : 294, comme le cliquet
`RENVOIS_SANS_TEXTE`. L'Agirc et l'Ircantec portent chacune deux suites de
périodes, une par tranche : chaque renvoi se mesure dans la sienne. Un seul
n'a rien à mesurer : l'abattement de l'Agirc de 1955, où la période d'avant
renvoie à la même valeur.

**La mesure.** Pour chaque renvoi, une copie du paquet `moteur/donnees.json`
change le renvoi sur sa seule série, dans sa seule suite. Un renvoi sans
valeur de repli (153) prend la valeur de la période d'avant, ou le défaut
de `INTERRUPTEURS` s'il ouvre sa suite, et la pension se compare à celle du
paquet du jour. Un renvoi à repli (âge d'ouverture, âge du taux plein,
durée requise : 141) est ôté dans les deux paquets comparés, son repli
rempli s'il manque (150 trimestres avant 1994 et 160 ensuite ; 60 ans
d'ouverture, celle du régime général depuis l'article 63 de l'ordonnance
du 19 octobre 1945 ; 65 ans de taux plein ; aucun âge d'ouverture n'a eu à
être rempli), puis décalé
d'un trimestre dans le second : c'est l'effet d'une règle fausse d'un
trimestre, et non de l'absence de la règle. Ôter le renvoi de la durée
requise du régime général sans repli changeait bien davantage : le
salarié non cadre né en 1929, entré à 18 ans et parti en 1984 à 55 ans,
passait de 8 053 € à 5 880 € par an. Soixante carrières simples de
l'affiliation type du régime, le premier statut de son inventaire (le
salarié non cadre pour le régime général et l'Arrco, le cadre pour
l'Agirc), passent au portage sur les deux paquets : départ l'année de la
bascule, l'année suivante, au milieu et à la fin de la série ; à 55, 60,
62, 65 et 67 ans ; début à 18, 22 et 30 ans.

**Le poids** est l'effectif de la population du régime fois l'écart relatif
moyen de la pension du scénario 1 sur ses soixante cas : chaque écart
plafonné à 100 %, chaque cas liquidé avant 1990 compté cent fois moins, la
somme divisée par le nombre de cas. Les effectifs sont ceux de la DREES
pour 2024 (`regimes/effectifs_retraites.csv`), et ceux des sections de la
CNAVPL au Recueil statistique 2024 de la CNAVPL (allocataires titulaires
de 2024 : Cipav 124 435, Carmf 92 648, Carpimko 85 107, CAVP 28 885,
CARCDSF 25 928, Cavamac 25 619, Cavec 11 991, CPRN 5 556, CARPV 4 767,
Cavom 3 047). Quatre sont des hypothèses, faute de chiffre lu : l'Agirc, un
quart des retraités d'Agirc-Arrco, et ses entreprises nouvelles la moitié
de ce quart ; l'Arrco tranche 2 des entreprises nouvelles, la moitié
d'Agirc-Arrco ; les artisans et les commerçants, chacun la moitié du régime
complémentaire des indépendants. Un régime sans effectif connu compte
mille.

**Ce que cela dit, et ne dit pas.** Le poids mesure l'enjeu d'un renvoi
juste, non le risque qu'il soit faux. Aucun départ n'est ouvert ni fermé
par le changement d'un renvoi parmi les cas mesurés.

**Le rangement simple : 100 renvois.** Ils ne changent aucun des soixante
cas : 26 retraits et 74 décalages d'un trimestre. Décalés d'un an, aucun de
ces 74 ne change davantage. Le moteur ne lit donc pas le champ pour ces
régimes : les complémentaires et les sections suivent l'âge et la durée du
régime de base, et sept régimes spéciaux (SNCF, RATP, IEG, Banque de
France, CRPCEN, Opéra, Comédie-Française) lisent d'abord leur durée propre
(`dureePropre`, leur table ou leur calendrier). Ces renvois se citent sans
mesure ni Catala, et leur rangement dira s'ils sont morts. Font exception
les huit renvois à la durée requise de l'Arrco, de l'Agirc, d'Agirc-Arrco
et de l'Ircantec : le moteur y lit la présence du renvoi, et l'ôter sans
repli calcule l'abattement à l'âge seul (18 cas sur 60 bougeaient à
l'Arrco). Ils ne bougent pas au décalage, mais leur rangement vérifie leur
date de début au texte. Les âges de 2011
de l'Agirc, de l'Agirc des entreprises nouvelles et de l'Ircantec bougent
au trimestre dans leur première suite, et sont classés (rangs 53, 98, 102
et 108) ; leur seconde suite ne bouge pas.

**Les biais repris.** La première mesure remettait à 1 % une série entière
selon sa fin, et non chaque cas selon son année ; la deuxième divisait par
la somme des poids, ce qui annulait la remise : les cas de 1946 et de
1973-1974 remontaient. Elle pesait une section de la CNAVPL, l'Agirc des
entreprises nouvelles, les artisans et les commerçants à l'effectif de
toute leur caisse. Elle prenait la première affiliation par ordre
alphabétique : le régime général et l'Arrco se mesuraient sur les chemins
de fer secondaires, l'Agirc sur le personnel navigant. Elle ôtait les
renvois à repli, ce qui mesure l'absence de la règle, non son erreur, et
ne change rien quand le repli dit la même chose que la fiche.

**Les trente plus lourds.**

| Rang | Régime | Renvoi | Depuis | Mesure | Cas qui bougent | Écart moyen | Effectif | Exemple (pension annuelle) |
|---|---|---|---|---|---|---|---|---|
| 1 | regime_general | `salaire_reference_par_generation` | 1994 | retrait | 33 sur 60 | 3,343 % | 14 744 736 | né en 1933, début à 22 ans, parti en 1995 à 62 ans : 14 245 € puis 13 048 € |
| 2 | regime_general | `decote_par_generation` | 1972 | retrait | 6 sur 60 | 1,582 % | 14 744 736 | né en 1943, début à 30 ans, parti en 2003 à 60 ans : 7 864 € puis 10 412 € |
| 3 | regime_general | `surcote_bareme` | 2004 | retrait | 12 sur 60 | 1,446 % | 14 744 736 | né en 1937, début à 18 ans, parti en 2004 à 67 ans : 18 793 € puis 21 689 € |
| 4 | agirc_arrco | `abattement_points` | 2019 | retrait | 34 sur 60 | 1,525 % | 12 795 748 | né en 1980, début à 30 ans, parti en 2035 à 55 ans : 13 833 € puis 16 006 € |
| 5 | arrco | `abattement_points` | 1961 | retrait | 27 sur 60 | 0,669 % | 12 795 748 | né en 1963, début à 30 ans, parti en 2018 à 55 ans : 9 175 € puis 10 697 € |
| 6 | fonction_publique_etat | `bareme_decote` | 2004 | retrait | 17 sur 60 | 4,917 % | 1 641 380 | né en 1949, début à 22 ans, parti en 2004 à 55 ans : 19 857 € puis 14 148 € |
| 7 | cnracl | `bareme_decote` | 2004 | retrait | 17 sur 60 | 4,671 % | 1 393 246 | né en 1949, début à 22 ans, parti en 2004 à 55 ans : 18 037 € puis 12 851 € |
| 8 | regime_general | `duree_requise_par_generation` | 1983 | un trimestre | 27 sur 60 | 0,391 % | 14 744 736 | né en 1975, début à 22 ans, parti en 2035 à 60 ans : 24 194 € puis 22 920 € |
| 9 | msa_salaries | `salaire_reference_par_generation` | 1994 | retrait | 33 sur 60 | 3,374 % | 1 678 770 | né en 1933, début à 22 ans, parti en 1995 à 62 ans : 14 067 € puis 12 870 € |
| 10 | msa_non_salaries | `bareme_points` | 1990 | retrait | 51 sur 60 | 5,108 % | 1 023 064 | né en 1943, début à 30 ans, parti en 2008 à 65 ans : 12 152 € puis 9 987 € |
| 11 | ircantec | `abattement_points` | 1971 | retrait | 29 sur 60 | 2,451 % | 2 108 941 | né en 1948, début à 30 ans, parti en 2003 à 55 ans : 6 087 € puis 7 576 € |
| 12 | regime_general | `duree_proratisation_par_generation` | 1994 | retrait | 8 sur 60 | 0,335 % | 14 744 736 | né en 1940, début à 22 ans, parti en 1995 à 55 ans : 5 754 € puis 5 555 € |
| 13 | msa_non_salaries | `meilleures_annees_non_salaries` | 2026 | retrait | 60 sur 60 | 4,769 % | 1 023 064 | né en 1959, début à 18 ans, parti en 2026 à 67 ans : 34 143 € puis 30 260 € |
| 14 | msa_non_salaries | `surcote_points` | 2004 | retrait | 22 sur 60 | 3,795 % | 1 023 064 | né en 1952, début à 18 ans, parti en 2019 à 67 ans : 24 032 € puis 18 951 € |
| 15 | organic | `salaire_reference_par_generation` | 1994 | retrait | 45 sur 60 | 5,08 % | 601 234 (hypothèse) | né en 1933, début à 30 ans, parti en 2000 à 67 ans : 11 146 € puis 10 052 € |
| 16 | rsi | `salaire_reference_par_generation` | 2006 | retrait | 42 sur 60 | 2,351 % | 1 202 469 | né en 1939, début à 30 ans, parti en 2006 à 67 ans : 17 523 € puis 16 440 € |
| 17 | msa_salaries | `decote_par_generation` | 1972 | retrait | 6 sur 60 | 1,582 % | 1 678 770 | né en 1943, début à 30 ans, parti en 2003 à 60 ans : 7 864 € puis 10 412 € |
| 18 | msa_salaries | `surcote_bareme` | 2004 | retrait | 12 sur 60 | 1,456 % | 1 678 770 | né en 1937, début à 18 ans, parti en 2004 à 67 ans : 18 594 € puis 21 490 € |
| 19 | cancava | `salaire_reference_par_generation` | 1994 | retrait | 45 sur 60 | 4,063 % | 601 234 (hypothèse) | né en 1933, début à 30 ans, parti en 2000 à 67 ans : 13 965 € puis 12 871 € |
| 20 | cipav_complementaire | `cotisation_par_classes` | 1979 | retrait | 54 sur 60 | 18,777 % | 124 435 | né en 1945, début à 30 ans, parti en 2000 à 55 ans : 5 976 € puis 3 361 € |
| 21 | rsi | `decote_par_generation` | 2006 | retrait | 16 sur 60 | 1,84 % | 1 202 469 | né en 1946, début à 30 ans, parti en 2006 à 60 ans : 8 070 € puis 9 965 € |
| 22 | fonction_publique_etat | `surcote_bareme` | 2004 | retrait | 11 sur 60 | 1,238 % | 1 641 380 | né en 1939, début à 18 ans, parti en 2004 à 65 ans : 25 582 € puis 29 420 € |
| 23 | cnracl | `surcote_bareme` | 2004 | retrait | 11 sur 60 | 1,238 % | 1 393 246 | né en 1939, début à 18 ans, parti en 2004 à 65 ans : 21 964 € puis 25 258 € |
| 25 | rsi | `duree_proratisation_par_generation` | 2006 | retrait | 29 sur 60 | 1,318 % | 1 202 469 | né en 1942, début à 30 ans, parti en 2007 à 65 ans : 17 231 € puis 16 387 € |
| 26 | regime_general | `age_taux_plein_par_generation` | 1983 | un trimestre | 6 sur 60 | 0,092 % | 14 744 736 | né en 1947, début à 30 ans, parti en 2009 à 62 ans : 12 872 € puis 12 637 € |
| 27 | rco_artisans | `abattement_points` | 2008 | retrait | 25 sur 60 | 2,263 % | 601 234 (hypothèse) | né en 1957, début à 30 ans, parti en 2012 à 55 ans : 8 267 € puis 9 358 € |
| 28 | msa_salaries | `duree_requise_par_generation` | 1994 | un trimestre | 32 sur 60 | 0,741 % | 1 678 770 | né en 1975, début à 22 ans, parti en 2035 à 60 ans : 24 194 € puis 22 920 € |
| 29 | organic | `surcote_bareme` | 2004 | retrait | 10 sur 45 | 2,039 % | 601 234 (hypothèse) | né en 1937, début à 18 ans, parti en 2004 à 67 ans : 15 223 € puis 17 652 € |
| 30 | regime_general | `age_ouverture_par_generation` | 1994 | un trimestre | 6 sur 60 | 0,081 % | 14 744 736 | né en 1970, début à 18 ans, parti en 2035 à 65 ans : 37 992 € puis 37 655 € |
| 31 | rci | `abattement_points` | 2013 | retrait | 32 sur 60 | 0,986 % | 1 202 469 | né en 1980, début à 30 ans, parti en 2035 à 55 ans : 14 000 € puis 15 796 € |

Le rang 24, la décote annulée par la durée du régime général, ne fait
bouger que des pensions liquidées avant 1990 : il cède sa place au rang 31. Les lots suivent
cet ordre, six par six. Les rangs 24 et 32 à 194 attendent le point
d'arrêt ; le tableau complet est dans les fichiers du projet.
