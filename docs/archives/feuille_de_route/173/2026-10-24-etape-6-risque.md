# L'étape 6 : Pourquoi changer, la même chose en moins de mots

**La demande.** Lot du 24 octobre 2026, deuxième vague : le propriétaire
demande une session par tâche, menée sans lui, dix en même temps ; celle-ci,
seule du lot sur les pages, mène l'étape 6 de l'action 173 : « Pourquoi
changer, moins de mots sans perdre une idée ».

**Ce qui se lit sans déplier.** Le budget de lecture de Pourquoi changer
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 650 à 560 mots de prose,
et de 270 à 180 dans les tableaux, qui en montraient 177 et n'ont pas changé.
Vu rouge à 560 pour 636, la page en montre 558. Partent : du résumé « En
clair », le premier prélèvement de la fiche de paie, que la première carte dit
et chiffre ; de cette carte, « au salaire moyen » redit pour la carrière
entière ; de sa source, la « carrière de référence » qu'elle décrit aussitôt ;
de la source de la seconde, la conversion des milliards, dite en huit mots au
lieu de dix-huit ; de « Ce que nous proposons d'en faire », l'annonce des
« trois choses » qu'elle énumère ; sous « Pour aller plus loin », la phrase qui
annonçait les dépliants, que le plan nomme. Trois titres raccourcissent, dans
le plan comme sur leur dépliant : « Les plus pauvres y perdent le plus »,
« selon le COR lui-même », « huit objections, huit réponses » — ce dernier tenu
par `test_la_page_risque_range_ses_sections_et_se_relie`, qui compte les huit
intertitres. Le résumé disait « ce qu'on leur promet » des enfants, pour ce
qu'on promet au lecteur : il dit « ce qu'on vous promet ».

**Ce qui se lit en dépliant.** `BUDGETS_DEPLIES` prend Pourquoi changer à son
adresse, `/risque` : 5 128 mots, vu rouge pour 4 950 ; 4 935 après. Les
dépliants finissaient souvent sur une phrase qui redisait leur chiffre ou leur
phrase en gras : la taxation implicite de 80 % qui « n'a pas besoin d'autre
explication pour faire partir tôt », l'épargne qui ne suit plus l'allongement
de la vie, la redistribution dont un tiers revient au sommet, les 75 milliards
d'allègements qui disent un barème « si lourd qu'il faut le neutraliser ».
Sous l'incidence, la retraite, cotisation la plus contributive, au report le
plus complet : le report de 100 % des cotisations de retraite complémentaire
le montre deux paragraphes plus haut. Sous « Ce qui arrive quand on attend
trop longtemps », les pays qui ont ajusté « quand ils ne pouvaient plus »
redisaient ceux qui n'ont pas ajusté tant qu'ils pouvaient attendre. Aucun
chiffre n'est récrit, aucune phrase en gras ne change, aucune simulation ne
bouge : seul le témoin de la page change.

**Ce qui se lit ensemble.** `COTE_A_COTE` (`tests/test_ecrans.py`) prend
Pourquoi changer : vert d'emblée, aucun de ses deux tableaux n'ayant de rangée
à deux valeurs.

**Ce qui ne se voyait pas, trouvé en chemin.** À 320 et 390 points, le tableau
de la seconde carte, ce que le système verse et encaisse de 2025 à 2070, se
repliait en rangée, trois valeurs côte à côte : « 14,1 % · 422 Md € », plus
large que sa colonne, passait sur la suivante, et l'on lisait « 422 Md€13,9 % ».
Le pli (`ajusterLePli`, `index.html`) passe en fiche un tableau plus large que
son cadre ; celui-ci ne l'était pas : ses colonnes se partagent la largeur, et
seule la case débordait. `test_aucune_case_de_tableau_ne_deborde_sur_sa_voisine`
mesure chaque case : vu rouge sur ces dix cases, aux deux largeurs, les seules
du site. Le pli mesure désormais chaque case ; la fiche range « Pensions
versées » et « Recettes » côte à côte à 390 points, l'une sous l'autre à 320.

**Laissé tel quel.** Les tableaux ; les trois repères de tête et leurs
étiquettes, que le parcours de présentation lit (`test_parcours.py`) ; le
chapeau de l'affiche, qui redit le premier repère pour qui ne lit que deux
lignes, et que `test_la_page_risque_chiffre_le_prelevement_depuis_le_modele`
suit ; les citations du COR, tenues à la lettre ; ce qu'un dépliant redit d'un
autre, parce qu'on en ouvre un seul — les huit objections reprennent le coin
socio-fiscal, l'effet récessif, la pension relative, la pauvreté des retraités
et le rendement de la génération 2000, que d'autres dépliants détaillent ; la
bibliographie.
