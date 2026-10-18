# Les carrières du parcours

**Le 18 octobre 2026, la demande.** La session d'orchestration, sur la
consigne du propriétaire, « Fait toutes les tâches qui n'ont pas besoin de mes
décisions » : les chiffres à unité du parcours, ses carrières d'abord.

**La mesure `simulateur`** (`scripts/mesures_prose.py`) dit ce que la page
Simuler affiche pour une saisie, à l'arrondi de l'écran. La page se rend par
le portage, une fois par saisie, comme `tests/test_parcours.py` la rend pour
confronter le parcours. Sur chaque ligne, elle lit la pension, le salaire, ce
que les recettes paient vraiment, le gain du salaire, l'écart au système
actuel et la part payée ; sous « Et pendant que vous cotisez », le gain jusqu'au
départ et les années qui l'en séparent. Ses réglages sont ceux de l'adresse,
et `montants=net` seul désigne l'exemple. Son test, dans `tests/test_prose.py`,
porte sur une page posée à la main.

**Ce qui est ancré.** Les quatre tableaux de carrières, 22 chiffres. De
l'exemple : le troisième chiffre et sa part payée, les quatre chiffres de sa
fiche de paie, et ses années, qui s'écrivaient « treize ». L'âge légal de la
proposition, deux fois, la garantie et son âge, sur les paramètres que le
README cite déjà ; le taux de l'État, sur la cellule que la méthodologie lit.

**Ce qui avait dérivé.** Le tableau de l'exemple, sous aucune adresse, ne se
confrontait à rien et datait du 20 septembre : 2 807 € pour 2 754 au système
actuel, −29,9 % pour −20,4 % à la proposition. `--corriger` l'a récrit depuis
le modèle ; les trois carrières tombaient juste. Il se confronte désormais à
la page (`test_le_parcours_rejoue_l_exemple_du_simulateur`). L'exemption du
« 91 % », « que la page n'écrit pas », est retirée : sa glose l'écrit.

**La garde.** `test_aucun_tableau_de_carriere_ne_s_ecrit_a_la_main`, de la
suite rapide, refuse tout chiffre écrit à la main dans un tableau de
carrière, et toute ancre qui ne lit pas la saisie de l'adresse au-dessus de
son tableau : la saisie s'écrit deux fois, et une adresse changée seule
ferait dire au tableau la carrière d'avant.

**Ce qui reste écrit à la main dans les deux sections.** Les saisies — les
salaires tapés, et les départs à 64 ans — que l'adresse porte, et où une
ancre ne vit pas. Les taux de la proposition (18, 5 et 23 %, le « 28 » du
droit en vigueur), à ancrer avec ceux du Programme (`parametre`). Les 16 % de
la facture qui manqueraient en 2070, avec les chiffres de la section Coût.
En lettres : « un an », « une année », « un peu plus de la moitié »,
« soixante-deux » statuts. Et un mot : le parcours fait lire « financé », la
page écrit « vraiment payé ».

**Vérifié.** `tests/test_parcours.py` et `tests/test_prose.py` passent, sauf
deux rouges d'avant l'étape : les ancres du README, de la carte et de
l'intégration, et `docs/etat.md`, périmés par le paquet que 03cc40a n'a pas
refait et par la veille de 8eebc15, que GitHub refait. De même, dans la
suite rapide, les trois rouges de `test_micro_social.py`.
