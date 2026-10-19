# Étape 7, treizième partie : la prémisse du déficit, la page Coût relue sur sa survie, sa grille et ses vingtiles

**La demande.** Vague B du 19 octobre 2026, session 20 de la quatrième salve :
« Action 138, étape 7 : la prémisse du déficit », le point 1 de « Ce qui
reste » de la note « la date des cohortes du déficit » (étape 3).
`scripts/mortalite_population.py --deficit` disait encore la page Coût à la
mortalité générale, quand elle fait vivre chaque cas type, depuis le
17 octobre, au rythme de son vingtile et à nombre de décès égal (note « la
mortalité différentielle ») : sa documentation, son premier tableau et ses
colonnes « page » étaient à relire sur cette survie. En Python seul, le
script n'ayant pas de jumeau. Ni la mortalité des ex-invalides et sa phrase,
ni l'inapte recalé, qui restent à la session des pages.

**Ce que fait le script, désormais.** Il relit la page telle qu'elle est, et
trois écarts l'en séparaient, non un.

- *Sa survie.* Chaque couple porte celle que la page lui donne sous le
  diviseur par vingtile : la survie de la population de son diviseur, ou de
  la sienne pour l'inapte, chaque cohorte depuis son départ
  (`cout._survies`) ; les masses la prennent à nombre de décès égal, les cas
  types pesés par les poids de la page (`cout._survies_alignees`). Ce sont
  les fonctions de la page (`_couple`, `_masses`). Avant, la survie du
  vingtile rapportée à la population générale, sans aligner.
- *Sa grille.* Les 480 couples que la page pèse (`GRILLE_DU_COUT`, `GRILLE`
  du script), et non les 345 des treize cas types : il en perdait cinq,
  l'agent sédentaire de la CNRACL, les actifs et les super-actifs de l'État,
  l'inapte et l'ex-invalide de la Cnav, quand les poids de la page pesaient
  pourtant leur caisse.
- *Son vingtile.* Celui que le diviseur de la page donne à la carrière
  qu'elle construit, la somme de ses revenus cotisés rapportée à celle des
  salaires moyens (`_vingtiles`, `niveau_relatif`), et non celui du niveau
  écrit du cas type : 189 des 345 couples en changent ; le salarié au salaire
  moyen passe du treizième vingtile au quatorzième, au quinzième pour les
  générations de 1930 à 1945.

Les colonnes « page » mesuraient la page d'avant le 17 octobre : elles
disent désormais la mortalité générale, que la page ne compte plus que sous
la table commune, d'où partent les soldes du script. Le premier tableau dit
ce que la survie de la page déplace à diviseur commun ; le second, la baisse
de la dépense à cette survie, et, en regard, à la mortalité générale. La
documentation disait ce second chiffre « plus grand et faux » : il est plus
petit, stock compris, et l'était déjà le 20 septembre (3,2 à 4,1 % contre 3,6
à 4,3 %) ; les gros capitaux, que le diviseur baisse, y sont servis moins
longtemps. La colonne du solde ne se dit plus « le défaut du site », qui
compte aussi la survie.

**La mesure.** `python scripts/mortalite_population.py --deficit`, puis avec
`--depuis 2026`, sur `main` au 19 octobre (bb34630), avant et après, chaque
écart corrigé seul par un script de travail, non commité. Baisse de la
dépense des scénarios 2 à 6 en 2030, 2050 et 2070, de la plus petite à la
plus grande, et ce que le diviseur par vingtile ajoute à leur solde moyen de
2026 à 2070 :

| | Baisse de la dépense | Solde moyen, en points de PIB |
|---|---|---|
| Avant | 3,1 à 3,7 % | +0,15 à +0,41 |
| La survie de la page, seule | 3,1 à 3,7 % | +0,15 à +0,41 |
| Puis la grille entière | 2,5 à 3,1 % | +0,13 à +0,33 |
| Puis le vingtile de la carrière | 2,9 à 3,6 % | +0,15 à +0,39 |

L'alignement ne bouge presque rien : il multiplie tous les cas types d'une
cohorte par le même nombre, et la baisse, un rapport de masses, n'en sent que
le poids des cohortes entre elles. La grille entière la baisse : l'agent
sédentaire de la CNRACL, au dixième ou au onzième vingtile, l'inapte et
l'ex-invalide de la Cnav, du premier au septième, en ôtent chacun deux
dixièmes de point environ au scénario 2 en 2030, les actifs et les
super-actifs de l'État presque rien. Le vingtile de la carrière la relève :
173 des 189 couples qui en changent montent, d'un vingtile le plus souvent ;
seul le militaire descend. À la mortalité générale, la baisse serait de 2,5
à 3,4 %. Le premier tableau passe, pour la masse du système actuel, de
+2,4, +2,7 et +2,3 % en 2030, 2050 et 2070 à +2,2, +2,0 et +1,7 % ; le
rapport de masses des scénarios 2, 4 et 6 bouge de +0,0 à +0,7 % au lieu de
−0,2 à +0,9 %. Le flux seul, depuis 2026 : 0,6 à 0,9 % en 2030, 2,4 à 2,9 % en
2050, 2,8 à 3,1 % en 2070, et +0,11 à +0,27 point de solde moyen au lieu de
+0,11 à +0,29.

Contre la page elle-même, sous son défaut et sous la table commune
(`calculer_cout` sous les deux réglages, même `main`), l'interrupteur ajoute
au solde moyen +0,135 point au scénario 2, +0,331 au 4 et +0,288 au 6, où le
script dit +0,149, +0,356 et +0,302 : l'écart est ce que la survie déplace,
que la page compte et que le solde du script n'ajoute pas. Aux scénarios 3
et 5, la page dit +0,019 et +0,093, le script +0,326 et +0,386 : voir plus
bas.

**Les tests** (`tests/test_mortalite_population.py`, suite rapide) :
`test_chaque_cas_type_vit_comme_la_page_le_fait_vivre_a_nombre_de_deces_egal`,
deux cas types posés à la main, l'un vivant un dixième de plus que la pyramide
chaque année depuis son départ, l'autre un dixième de moins, pesés un quart et
trois quarts — à pension égale la masse ne bouge pas, à pension triple celui
qui vit longtemps la grossit, seul de sa grille un cas type vit comme la
pyramide ; `test_l_inapte_vit_comme_les_inaptes_de_la_cnav_sous_le_diviseur_de_son_vingtile`,
trois courbes posées à la main ;
`test_chaque_couple_a_le_vingtile_que_la_page_donne_a_sa_carriere`, le
salarié au salaire moyen de 1965 contre le convertisseur du défaut ;
`test_la_grille_est_celle_que_la_page_pese`. Chacun vu rouge sur le
comportement : la forme neuve du script d'abord écrite sous les règles
d'avant — 232,2 têtes où la pyramide en garde 262, l'inapte à la survie de
son vingtile, le treizième vingtile pour le quatorzième, les seuls cas types
—, puis corrigée. Le test des dates garde ses dates et laisse sa survie au
premier.

**Trouvé en chemin.** Aux scénarios 3 et 5, le script applique le rapport
des diviseurs à toute la pension, quand ils gardent au stock d'avant la
bascule le droit en vigueur (`ScenarioNotionnel._deja_liquide`), et que les
droits acquis à la bascule entrent au compte par le diviseur de leur vingtile
et en sortent par lui (`_droits_acquis`) : seul le compte ouvert à la bascule
le sent pour l'essentiel. Leur baisse en est grossie, d'environ 0,3 point de
solde moyen contre la page. La documentation du script le dit.

**Ce qui reste**, dans l'ordre :

1. *Le déficit des scénarios 3 et 5*, une session, en Python seul :
   n'appliquer le rapport qu'à la part du compte ouverte à la bascule, que la
   grille ne garde pas (`capital_droits_acquis` et `capital_notionnel` de la
   simulation), puis remesurer contre la page.
2. *Les poids de chaque année.* Le script pèse toutes les années aux poids
   de la dernière année observée (`Cout.poids`), quand la page les recale
   chaque année sur les groupes du COR (`_poids_par_groupe`) ; non mesuré.
3. *La limite, à la fin de l'étape* (note « la mortalité différentielle »,
   point 4) : le récit de `docs/limites/5-hors-du-modele.md`, vrai à sa
   date, dit une baisse de 3,5 à 4,4 %, deux à cinq dixièmes de point de solde
   moyen, et la page à la mortalité générale ; le paragraphe d'état pourra
   dire 2,9 à 3,6 % et 0,15 à 0,39 point, moins aux scénarios 3 et 5, et une
   survie qui déplace le rapport de masses de moins de 1 %.
4. *Le bloc de l'étape 3* nomme encore « à l'étape 7, la prémisse du
   déficit » : c'est fait, et la session de l'étape 3 qui le récrira l'ôtera.
