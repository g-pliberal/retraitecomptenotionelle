# Les lignes du portage sans test : la mesure refaite contre la suite entière, quatre fichiers classés, deux fichiers de tests, un défaut du relevé

**Reprise, au 12 novembre 2026.** Les quatre fichiers que l'inventaire
disait les moins couverts sont classés, ligne par ligne, et n'appellent plus
rien : deux fichiers de tests neufs tiennent la fusion et le journal, le
reste est déjà tenu, ou le sera quand les tests du moteur Python passeront
au portage. La mesure a montré que le classement de départ trompait : les
lignes qu'aucun test n'exécute sont ailleurs, 1 839 dans les 65 paires. Il
reste à classer de même les fichiers suivants, dans l'ordre de la table « Ce
qui reste » : d'abord `compte.js`, dont une branche entière ne tourne dans
aucun test, puis `droit/completer.js`, `droit/reversion.js`,
`droit/liquider.js`. Par quoi commencer : refaire la mesure, par la recette
de la même section, puis lire la table. Un défaut du relevé attend une
décision du propriétaire, section « Le défaut ».

**La demande.** Fixer par des tests ce que la concordance n'exécute pas, sur
les fichiers du portage les moins couverts — `droit/releve.js` (21 %),
`journal.js` (60 %), `droit/categories.js` (67 %), `fusion.js` (78 %) —, après
avoir mesuré si ces lignes sont déjà tenues ailleurs, ou le seront par le
lot D de l'inventaire.

## La pertinence : la mesure de départ ne comptait qu'une partie des tests

`python scripts/jumeaux.py --couverture`, refait au commit `3944fdc`,
retrouve le constat : `releve.js` 21,0 %, `journal.js` 59,6 %,
`categories.js` 67,4 %, `fusion.js` 78,3 %. Mais cette mesure ne rejoue que
les essais de `tests/js/`, la fabrication des témoins, et les tests pytest
dont le nom porte « javascript », « portage » ou « jumeau ». Or des
confrontations entières s'appellent autrement :
`test_les_deux_moteurs_ecrivent_les_memes_etapes` (`tests/test_droit.py`),
qui fait écrire au portage le relevé d'un témoin sur cinq, ou les tests de
`tests/test_taux_plein_a_soixante_cinq_ans.py`, qui passent par le pont
(`droit_et_refait`).

J'ai donc rejoué la suite complète sous la couverture de V8
(`NODE_V8_COVERAGE`, que tout node lancé par un test hérite), sans mémoire
des calculs, et relu le résultat par `jumeaux.lire_v8`.

| | lignes de code | jamais par la concordance | par aucun test |
|---|---:|---:|---:|
| tout `moteur/js/` | 53 260 | 7 515 | 4 551 |
| les 65 paires | 30 277 | 2 988 | 1 839 |
| dont les 18 paires de données | 5 174 | 628 | 611 |
| dont les 47 autres | 25 103 | 2 360 | 1 228 |
| `droit/releve.js` | 334 | 264 | 7 |
| `journal.js` | 94 | 38 | 19 |
| `droit/categories.js` | 218 | 71 | 7 |
| `fusion.js` | 157 | 34 | 34 |

Des 407 lignes des quatre fichiers que la concordance n'exécute pas, 340
tournent déjà dans un autre test ; 67 ne tournent dans aucun. Le classement
par la concordance ne désignait donc pas les bons fichiers : `releve.js`, le
premier de la liste, est l'un des mieux exécutés.

**Les limites de la mesure.** Elle dit qu'une ligne est exécutée, non qu'un
test en vérifie le résultat. La passe a tenu 77 minutes et je l'ai
interrompue à 99 %, sur des tests du coût qui relancent le pont à chaque
demande : 8 094 tests passés, quelques dizaines au plus non joués. Deux tests
y étaient rouges, sans rapport : l'un tient à la mémoire coupée, et passe
sans elle ; l'autre, le tableau de bord périmé, l'est sur `main`, par des
fiches qu'une autre session a ajoutées, et GitHub le refait. `routeur.js`
(2 138 lignes) reste à zéro : il ne tourne que dans le navigateur, que
`tests/test_ecrans.py` pilote et que V8 ne voit pas d'ici. Le côté Python,
enfin, n'est mesuré que pour les quatre jumeaux, par leurs six fichiers de
tests sous la sonde de `jumeaux.py` : la seconde passe de la suite entière a
fait redémarrer le conteneur, et je ne l'ai pas relancée.

## Les quatre fichiers, ligne par ligne

« Lot D » veut dire : la ligne jumelle du Python est exécutée par un test
qui n'éprouve que le Python, et qui passera au portage avec ce lot.

| fichier | lignes | classement |
|---|---|---|
| `droit/releve.js` | 67-195, 340-437 (`donnees`, `lignes`, les faits) | déjà tenues : `test_les_deux_moteurs_ecrivent_les_memes_etapes`, et `lignes_consommees` de la liquidation |
| | 265-333 (`pointsDeLAnnee`, `revenuDesPoints`) | déjà tenues : `tests/test_releve_lu.py`, par `tests/js/lire-releve.mjs` |
| | 270-271, 300-301 (aucun régime de l'étage ; étage non converti) | lot D : `tests/test_revenu_des_points.py` |
| | 304-305 (seize plafonds sous deux euros) | inatteignable |
| | 412 (aucun fait ne couvre l'année) | atteinte par deux témoins sur 932 : le défaut ci-dessous |
| `journal.js` | 62-75, 78-79, 148-150 (`donnees`) | déjà exécutées : les confrontations qui passent par `tests/js/comparer-liquidation.mjs`, dont `test_les_deux_moteurs_liquident_et_journalisent_a_l_identique` |
| | 97-101, 113-115, 126-128 (les refus, la longueur, l'état à une date) | lot D : `tests/test_liquidation.py`, lignes 368 à 401 |
| | 117-123 (`entree`) | lot D, un seul appel, sans le refus |
| | 76-77 (`annule`) | sans test, des deux côtés |
| `droit/categories.js` | 172-185, 235-236, 258-300, 319 (le parent de trois enfants, le fonctionnaire) | déjà tenues : `tests/test_taux_plein_a_soixante_cinq_ans.py`, par le pont, valeurs tirées des textes |
| | 39-41, 67-68, 100-101, 340 | déjà exécutées par la suite ; je n'ai pas cherché par quel test |
| | 57-58, 63, 71-72 (les paliers des anciens combattants) | lot D : `tests/test_taux_plein_par_categorie.py`, lignes 75 à 116 |
| | 213-214 (carrière sans départ) | inatteignable |
| `fusion.js` | 88-94, 179-180 (« le plus élevé ») | lot D : `tests/test_moteur.py`, ligne 1285 |
| | 112-113, 159-160, 173-176, 181-194 (les refus, le pivot absent, « le plus faible », la moyenne) | sans test, des deux côtés |
| | 133-135 (aucune durée requise : 172 par défaut) | inatteignable |

**Ce que « déjà tenues » vaut.** Pour `releve.js`, les tests qui exécutent
le portage sont des confrontations au jumeau : la valeur attendue est celle
du Python. Ce qui vient d'une source — le contrat C.5, le fait que chaque
ligne cite, le revenu le plus bas qui ouvre des points — n'est affirmé que
sur le Python (`tests/test_droit.py`, lignes 171 à 269 ;
`tests/test_revenu_des_points.py`). Le jour où le jumeau part, ces
confrontations n'ont plus d'attendu : c'est le lot D qui doit porter ces
affirmations, et rien d'autre ne les tiendra. Le pont n'expose ni
`Releve.lignes`, ni `revenuDesPoints`, ni `ageDesAnciensCombattants`, ni le
journal, ni `fusionner` : pour ces tests, « porter au pont » voudra dire une
entrée de plus dans `LECTURES_DU_DROIT`, ou un essai de `tests/js/`.

**Le lot D et les deux fichiers nommés.** `tests/test_simulateur.py` ne lit
ni `releve`, ni `categories`, ni le journal ; il lit le régime fusionné
(ligne 974), sous la règle par défaut. `tests/test_reversion.py` lit le
journal de l'échéancier (lignes 3344 à 3412, 3679) et les durées d'un relevé
(ligne 3412), jamais ses lignes ni les catégories. Ces deux fichiers ne
couvriront donc aucune des 67 lignes : ce sont quatre autres fichiers qui le
feront, ceux de la table.

## Ce qui est écrit

Deux fichiers de tests du portage, que `test_web.py` lance avec les autres
essais de `tests/js/`. Aucune valeur attendue n'y vient du moteur.

- `tests/js/fusion.test.js`, sept tests, sur un catalogue de sept régimes
  posé à la main, aux taux ronds. La source est `docs/methodologie.md`,
  § 7 : le plus défavorable paramètre par paramètre, la somme des taux du
  pivot, et les trois autres critères de `critere_taux`. Le portage ne
  fusionnait que sous la règle par défaut ; les autres critères ne tournaient
  qu'en Python, pour la prose (`mesures_prose.py`, « fusion?critere=… », les
  41,2 % de la méthodologie) et pour `scripts/solde_fusion.py`. Ces lignes
  deviennent vivantes le jour où ces deux scripts passent par le pont.
- `tests/js/journal.test.js`, neuf tests. La source est
  `docs/architecture.md`, § 7.4 et annexe C.8 : on ajoute sans effacer, les
  deux lectures, la lignée, l'extinction par une entrée sans montant, les
  champs qui manquent par défaut. Il redit en JavaScript les deux tests du
  journal de `tests/test_liquidation.py` : le lot D n'aura qu'à retirer leur
  moitié Python.

Après eux, il ne reste dans `journal.js` aucune ligne sans test, et dans
`fusion.js` que les trois lignes inatteignables. Aucun de ces tests n'a
rougi : le portage fait ce que ses sources disent.

**Ce qu'un test ne fait que figer.** Rien. J'ai écarté deux cas faute de
source. La moyenne (`moyenne_ponderee`) compte une fois chaque période
active, donc deux fois un régime à deux tranches, et n'est pondérée par
rien, malgré son nom ; `solde_fusion.py` la dit « la moyenne des taux de tous
les régimes ». Le test la pose sur un catalogue où chaque régime n'a qu'une
période, où les deux lectures donnent le même nombre. Et les 172 trimestres
par défaut, que rien ne source, ne sont pas testés.

**Vérifié sans rien écrire.** Pour les lignes que le lot D portera, j'ai
passé au portage, à la main, les valeurs des tests Python tirées des
textes : les dix-neuf cas des anciens combattants (décret n° 74-54 ;
circulaire Cnav n° 2024-29) et les dix-sept du revenu que des points
supposent. Tous conformes : aucun défaut n'attend le lot D sur ces lignes.

## Le défaut : une période assimilée n'est citée par aucune ligne du relevé

Le contrat C.5 dit le champ `fait` obligatoire : « le fait qui ouvre le
droit » (`data/reference/contrats/ligne_releve.yaml`, ligne 36). Le relevé
de tous les témoins, 239 189 lignes sur 932 requêtes, le respecte sauf sept
fois, sur deux témoins : `assimilee_sportive_de_haut_niveau` (les durées du
régime général de 2012 à 2016) et `assimilee_tuc_avant_l_embauche` (1985 et
1986). Ces années ne portent qu'une période assimilée déclarée, le fait
`assimilee_1` de la chronologie ; or `Faits` ne retient que les périodes
d'activité et d'interruption (`releve.js`, lignes 375-376 ; `releve.py`,
lignes 417-418). La ligne sort sans fait, donc sans la présomption ni la
fiabilité de sa période. Aucun montant n'en dépend.

Pour le voir : passer les 932 requêtes de `tests/temoins/simulations.json` à
`tests/js/comparer-droit.mjs`, et compter les lignes de `releve.lignes` sans
`fait`. La confrontation des deux moteurs ne le voit pas : elle ne prend
qu'un témoin sur cinq, plus ceux des enfants.

Je ne l'ai pas corrigé, et n'ai commité aucun test rouge. La correction
n'est pas courte : les trimestres assimilés se cumulent par fiche et par
année (`trimestresDesPeriodes`, dans `compter.js`), sans garder le fait
d'où ils viennent, et plusieurs périodes peuvent nourrir la même année. Il
faut soit porter l'identifiant du fait jusqu'aux durées, soit donner aux
périodes assimilées leurs propres lignes, avec la fiche et la version
qu'elles connaissent et que le relevé perd aujourd'hui, comme le font les
trimestres des enfants. C'est un choix sur la forme du relevé, dans quatre
fichiers du droit (`compter` et `releve`, des deux côtés), hors du périmètre
de cette étape.

## Le code qui paraît inatteignable

Laissé en place, pour la session qui mesure le code mort.

- `droit/releve.js`, lignes 303 à 305 : seize plafonds valent toujours plus
  de deux euros ; la série rend 16 dès 1900.
- `droit/categories.js`, lignes 212 à 214 : `regleDuParent` n'est appelée
  qu'à la liquidation, qui a toujours une date d'effet.
- `fusion.js`, lignes 132 à 135 : le catalogue porte toujours une durée
  requise ; le Python le dit (`pragma: no cover`).
- `journal.js` : `etatAu`, `entree`, `length` et le champ `annule` n'ont
  aucun lecteur ni écrivain dans le portage, et `annule` n'en a aucun en
  Python non plus. Le contrat C.8 les décrit, les tests neufs les tiennent ;
  le moteur ne lit le journal que par `servi` et `donnees`.

## Ce qui reste

Les lignes qu'aucun test n'exécute, dans les paires, au commit `3944fdc`,
hors des fichiers exclus de cette étape :

| fichier | lignes | à regarder d'abord |
|---|---:|---|
| `regimes.js` | 162 | des refus de deux lignes, partout ; 2770-2782 |
| `patrimoine.js` | 121 sur 150 | tout le module : aucun test ne l'appelle |
| `droit/completer.js` | 106 | 1199-1221 |
| `chronologie.js` | 100 | 1250-1257 |
| `droit/reversion.js` | 90 | 737-745 |
| `remuneration.js` | 84 | 1421-1429 |
| `droit/liquider.js` | 81 | 2823-2832, 3034-3042 |
| `compte.js` | 81 | 461-484 et 960-974 (l'acquisition commune, sous `taux_cotisation_uniforme`, et la réunion des intervalles d'assiette), 493-501, 729-739 |
| `carriere.js` | 74 | 2462-2466 |
| `mortalite.js` | 65 | |
| `droit/compter.js` | 60 | |
| `droit/ouvrir.js` | 52 | |
| `tva.js`, `distribution.js`, `effectifs.js` | 46, 41, 24 | presque tout le module |

La plupart sont des blocs de deux ou trois lignes, un refus ou un retour
nul. Les blocs longs sont les vrais candidats ; `compte.js` porte le plus
net, une branche du compte notionnel qu'aucun test ne fait tourner. Les
modules de données presque entiers (`patrimoine.js`, `tva.js`,
`distribution.js`, `effectifs.js`) relèvent plutôt du code mort : les 18
paires de données gardent 611 lignes que rien n'appelle.

**La recette de la mesure**, une heure et quart :
`NODE_V8_COVERAGE=<dossier> CALCULS_SANS_MEMOIRE=1 FABRIQUE_SANS_MEMOIRE=1
python -m pytest -q`, puis `jumeaux.lire_v8(<dossier>,
jumeaux.fichiers_suivis())`, dont on retire les lignes que
`.cache/jumeaux/couverture.json` dit déjà couvertes. Les node du pont
n'écrivent leur couverture qu'en se fermant : interrompre pytest par
`SIGINT`, jamais par `SIGKILL`.

## Ce que le propriétaire tranche

1. *Le défaut du relevé* : citer le fait de la période assimilée sur la
   ligne de l'année, ou donner aux périodes assimilées leurs lignes, avec
   leur fiche et leur version. La seconde forme dit plus, et change les
   lignes du relevé ; aucune ne déplace un montant.
2. *La mesure de la carte* : `jumeaux.py --couverture` ne compte que les
   tests nommés « javascript », « portage » ou « jumeau », et classe mal.
   Lui faire rejouer la suite entière coûte une heure et quart ; élargir son
   filtre aux tests qui passent par le pont coûterait moins. Je n'ai pas
   touché au script.
3. *Les tests du lot D que le pont ne sait pas servir* — le relevé en
   lignes, le revenu des points, les paliers des anciens combattants : une
   entrée du pont chacun, ou des essais de `tests/js/`, comme ici.
4. *La moyenne de la fusion* : par période ou par régime, pondérée ou non.
   Elle ne sert qu'à `solde_fusion.py`.
