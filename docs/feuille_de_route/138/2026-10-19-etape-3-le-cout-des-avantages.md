# Étape 3, treizième partie : le coût des avantages, chaque cohorte à la date et à l'âge que le droit de sa génération lui donne

**La demande.** Vague du 19 octobre 2026, session 4 de la première salve :
« Action 138, étape 3 : le coût des avantages » — le point 2 de « Ce qui
reste » de la note « la date de chaque cohorte ». `avantages.py` a sa propre
grille, qui faisait partir les cinq cohortes d'une génération à son âge, la
date décalée d'autant : la même erreur que `cout.py` a quittée le 18 octobre,
à corriger en Python et dans son portage. Ni les 0,19 point, ni l'Ircantec, ni
la page Coût.

**Le portage.** Le coût des avantages n'a pas de jumeau JavaScript : il ne se
calcule qu'en Python, et la page Droits non cotisés en lit la série figée dans
le paquet (`AvantagesFiges`, `agregats.js`), que GitHub refait à chaque envoi.
Rien n'est à porter : la page lira la série corrigée au premier paquet refait.

**Ce que fait la grille des avantages, désormais.** Chaque cohorte des
345 couples part l'année et à l'âge que le droit de sa génération donne au cas
type (`avantages._departs_des_cohortes`, `Pensionne.departs`,
`Pensionne.ages_depart`), tirés de la boucle de la grille du coût
(`cout._carrieres_voisines`, que `cout._departs` emprunte désormais sans rien
changer à ce qu'il rend). Sa pension, et ce qu'elle porte d'avantages, restent
ceux de la génération simulée ; une cohorte que la grille ne sait pas simuler
part à l'âge de la grille, l'année décalée d'autant — quatre, nées de 1883 à
1893. Sur les 1 380 cohortes voisines, 101
partent une autre année, 34 un an plus tôt, 49 un an plus tard, les autres nées
avant 1930, sauf l'agent de conduite de la SNCF né en 1998 ou 1999, qui part en
2052 et 2053 et non en 2061 et 2062 ; 172 partent à un autre âge, telle la
cohorte de 1964 du salarié au SMIC, partie en novembre 2024 à 60 ans et 9 mois
au titre des carrières longues, quand la génération 1965 qui la représente
part à 61 ans, en 2026. `masses` compte chaque cohorte à partir de son départ ;
`masses_anticipees` aussi, et compte ses années précoces à son âge légal à
elle, celui de la génération dont le droit date le départ.

**Le prorata.** Dater chaque cohorte a montré une erreur que la grille
masquait. L'âge atteint se comptait à l'année, entier, et l'âge légal ne l'est
plus — 61 ans et 2 mois nés en 1953, 62 ans et demi en 1962 — : toute l'année
où une cohorte atteint son âge légal passait avant lui, si bien qu'une cohorte
partie à l'heure devenait anticipée l'année de son départ. La carrière
interrompue née en 1962, partie en août 2024 à 62 ans et demi, son âge légal,
devenait ainsi anticipée toute l'année 2024, rangée aux régimes spéciaux, le
motif par défaut d'un départ que rien n'ouvre ; avec les autres cohortes
parties à l'heure, et l'année entière comptée à celles qui atteignaient leur
âge légal en cours d'année, la série de 2024 passait de 8,2 à
17,6 milliards. Les générations de la grille, aux âges légaux ronds jusqu'à
1960 — 60 ans en 1950, 62 ans en 1955 et 1960 —, n'en montraient rien avant
2027, l'année des 62 ans de la génération 1965, à 62 ans et 9 mois. L'annuité
se compte désormais au prorata de l'année passée entre le départ et l'âge
légal ; l'année du départ ne compte plus que depuis le départ. Les masses,
elles, comptent toujours l'année du départ entière, ici comme dans la grille
du coût.

**La mesure.** Les pensions servies avant l'âge légal, en milliards d'euros
courants (`python scripts/cout_avantages.py --duree`), la grille datée de ses
deux façons :

| Avant l'âge légal | 1990 | 2006 | 2007 | 2010 | 2012 | 2014 | 2020 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| à la date de la grille | 3,9 | 7,3 | 6,6 | 6,5 | 6,5 | 12,7 | 9,9 | 8,2 | 8,2 |
| chacune à sa date, au mois | 3,7 | 7,0 | 7,1 | 6,5 | 7,5 | 10,0 | 10,3 | 9,9 | 10,6 |

| En 2024 | Carrière longue | Classement | Régimes spéciaux | Total | Part de la dépense |
|---|---|---|---|---|---|
| à la date de la grille | 1,9 | 4,0 | 2,3 | 8,2 | 1,9 % |
| chacune à sa date, au mois | 3,4 | 4,8 | 2,5 | 10,6 | 2,5 % |

Les cohortes que leur droit fait partir avant la grille ajoutent des années
précoces. La carrière longue ne creuse plus en 2023 et 2024, où la grille
faisait partir à 61 ans, en 2024 et 2025, les cohortes de 1963 et 1964 du
salarié au SMIC, que le droit de leur génération fait partir à 60 ans et à
60 ans et 9 mois : elle passe de 3,4 milliards en 2022 à 3,6 en 2023 et 3,4 en
2024, au lieu de 1,7 et 1,9. L'agent de catégorie active né en 1958 ou 1959
part à 61 ans et 2 mois, en 2019, et à 61 ans et 7 mois, en 2020, et non à
62 ans avec la génération 1960 ; né en 1948, à 59 ans et demi, en 2007, et non
à 60 ans, en 2008, avec la génération 1950. L'âge légal de chaque cohorte en
ajoute d'autres, que la grille, lisant celui de sa génération, ne comptait
pas : à 60 ans en 2012, la cohorte de 1952 passe neuf mois avant le sien,
60 ans et 9 mois — chez l'agent de catégorie active, le militaire, les agents
des IEG et de la SNCF — ; à 62 ans en 2024, celle de 1962 un semestre avant
62 ans et demi, chez les mêmes et le salarié au SMIC. Il en retire là où la
grille comptait trop : le pic de 2014 tombe de 12,7 à 10,0, la cohorte de
1953, à 61 ans, n'y passant que deux mois avant son âge légal, 61 ans et
2 mois, quand la grille lui en comptait douze, à l'âge légal de la génération
1955, 62 ans, chez les mêmes cinq cas types. Le prorata, enfin, ôte jusqu'en
2006 un tiers de milliard au plus : l'agent de catégorie active, parti à
59 ans et demi jusqu'à la génération 1945, passait toute son année de départ
avant l'âge légal de 60 ans, et n'en passe plus que la moitié. De 2008 à 2011,
rien ne bouge. Le total chiffré de 2024 passe de 99,6 à 99,9 milliards, 23,4 %
de la dépense ; les lignes que le modèle calcule encore, de 17,5 à 17,8 ; deux
lignes voisines, la majoration de la retraite proportionnelle et l'indemnité
temporaire de retraite, échangent leur rang dans la légende.

**Les tests.** En suite rapide,
`test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation`
(un couple posé à la main, le salarié au SMIC de 1965 : masses, années
précoces au prorata et à l'âge légal de chaque cohorte, la carrière
interrompue de 1962 partie à l'heure et jamais anticipée, la grille sans
dates) et `test_la_decomposition_date_chaque_cohorte_au_droit_de_sa_generation`
(le salarié au salaire moyen de 1963 à 1967, tiré de L. 161-17-3 : 2026, 2027,
2028, 2030, 2031, à 63 ans et demi puis à 64 ans). La confrontation au jaune
pensions de 2027 compte ses têtes à la date de chaque cohorte
(`Pensionne.liquidation`), et tient : le militaire part au même âge dans toutes
ses générations. Régénéré dans un worktree, le changement ne déplace aucun des
886 témoins de simulation, et 5 rendus de page sur 78 : Droits non cotisés, et
la page Coût en ses quatre états, par son seul encart des avantages ; dans le
paquet, rien que le coût des avantages. La suite complète y passe, jouée avant
l'envoi (5 416 tests). Les chiffres ancrés de `docs/limites/5-hors-du-modele.md`,
qui mesurent le modèle, sont corrigés ici ; ceux de
`docs/parcours_presentation.md`, qui lisent le paquet, GitHub les refait avec
lui. Le récit de `docs/avantages_non_contributifs.md` garde les siens, vrais à
leur date.

**Ce qui reste**, de cette partie ; les points 1 et 3 de la note « la date de
chaque cohorte » demeurent, le second valant aussi pour les avantages : une
cohorte qui part à une autre date touche la pension, et les avantages, de la
génération simulée.

1. *La même erreur, dans un script de l'étape 7* :
   `scripts/mortalite_population.py` relit la grille du coût à la date de la
   grille (`annee_liquidation + decalage`), et non à celle de chaque cohorte
   (`Pensionne.liquidation`). Un script de mesure, que nul test ne joue : à
   porter, avec le sien, par une session de l'étape 7.
2. *L'année du départ entière dans les masses*, celles du coût comme celles
   des avantages : la cohorte partie en novembre y compte toute l'année. Seules
   les années précoces se comptent au mois ; y porter les masses déplacerait
   le coût agrégé, une décision de modèle à mesurer d'abord.
3. *Pour une session des pages* : rien de neuf. La page Droits non cotisés
   lit la série du paquet, et sa phrase sur la carrière longue, « qui
   n'apparaît qu'après 2010 », reste vraie (2013).
