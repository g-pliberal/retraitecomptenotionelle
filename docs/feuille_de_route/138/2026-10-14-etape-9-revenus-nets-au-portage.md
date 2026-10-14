# Étape 9, dixième partie : les revenus nets au portage, et la convention du COR en JavaScript

**La demande.** Le premier reste de l'étape (bloc « Reprise » du 14 octobre,
note `2026-10-14-etape-9-portage-du-cycle-de-vie.md`) : les revenus nets des
indicateurs de cycle de vie, sous la convention du COR, en Python — fait —
puis dans le portage JavaScript de la nuit (`cycle-de-vie.js`), que node
rejoue contre le Python. L'impôt (étape 5) n'en est pas ; l'affichage attend
une session du site. Session du 14 octobre, une parmi dix-neuf.

**Ce qui est fait.**

- `moteur/js/prelevements-historiques.js`, le jumeau entier de
  `donnees/prelevements_historiques.py` : les séries datées, la moyenne des
  douze mois, les pensions (CSG, CRDS, CASA, maladie de chaque régime sur sa
  part), les salaires de chaque famille (privé, contractuel, agent public), les
  barèmes des indépendants (tranches, paliers, indemnité journalière, assiette
  de la CSG augmentée des cotisations jusqu'en 2024), et le net imposable. Une
  bizarrerie du Python est gardée telle quelle : une marche vide d'une série
  tenue avant sa première marche rend la première.
- Le paquet porte l'histoire sous `prelevements_historiques`
  (`scripts/construire_donnees.py`, `_prelevements_historiques`), telle que le
  chargeur du Python la lit ; vingt kilo-octets. La clé est lue avec un défaut :
  la version du paquet ne bouge pas.
- `moteur/js/remuneration.js` : `ficheDepuisBrut` et `indemnitesDesLignes`,
  jumeaux de `fiche_depuis_brut` et d'`indemnites_des_lignes`, que le portage
  n'avait pas.
- `moteur/js/cycle-de-vie.js` : `revenusNets` (la fiche du droit en vigueur,
  ramenée aux prélèvements hors retraite et aux contributions d'équilibre de
  l'année ; avec `proposition`, la fiche de la proposition après la bascule),
  `revenusImposables`, `prelevementsParAnnee`, `partsAssujetties`,
  `partsImposablesParAnnee`, `conventionCor`, `conventionNette` ;
  `fluxDesSystemes` porte les nets, une fiche par carrière et par fiche, comme
  `_cle_des_revenus`. Seul l'impôt reste refusé, par une erreur qui le nomme.
- `tests/test_cycle_de_vie_portage.py` : les sept carrières sous deux
  conventions de plus, la nette et celle du COR ; leurs revenus nets, nets
  avec la proposition, imposables, et les prélèvements de chaque année ; et une
  grille du module seul — huit familles, douze années de 1968 à 2026, quatre
  revenus, 732 valeurs —, qui couvre le contractuel, le commerçant, le libéral
  et l'avocat que les carrières n'ont pas. Tout se retrouve à 10⁻⁹ près, du
  premier coup ; un net faussé d'un millième est vu. Le fichier reste au niveau
  rapide (quatre secondes).
- `index.html` précharge le module, comme `test_web.py` l'exige : une ligne
  hors de la zone, que la suite demande.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'impôt au portage* (étape 5) : `impot_revenu.py` et
   `donnees/impot_revenu.py`, le barème dans le paquet, `impotsParAnnee`,
   `avecLImpot`, puis la convention après impôt. Le net imposable est prêt
   (`revenusImposables`, `partsImposablesParAnnee`), testé.
2. *Les âges de départ* (`depart`, `balayage`, `ages_de_depart`) et les âges
   d'équilibre d'un cas type, qui demandent les cas types du COR en
   JavaScript, ou une carrière du site à leur place.
3. *L'affichage*, avec l'étape 10, par la session du site : `pages.js` peut
   importer `conventionCor` et `indicateursDesSystemes`.
4. Puis, inchangés : la révision de 2026 et la rémunération moyenne par tête du
   COR, Typfallsmodellen au registre.
