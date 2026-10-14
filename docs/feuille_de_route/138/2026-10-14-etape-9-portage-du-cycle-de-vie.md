# Étape 9, neuvième partie : le portage JavaScript des indicateurs de cycle de vie, les flux bruts et l'âge d'équilibre

**La demande.** Le premier reste de l'étape (bloc « Reprise » du 10 octobre) :
les jumeaux JavaScript de `cycle_de_vie.py`, âge d'équilibre compris, de
`prelevements_historiques.py` et de `contributions_equilibre.py`, que node
rejoue contre le Python, sans toucher aux pages — l'affichage attend une
session du site, avec l'étape 10. Session de nuit du 14 octobre, une parmi
dix-huit.

**Ce qui est fait.**

- `moteur/js/contributions-equilibre.js`, le jumeau entier de
  `contributions_equilibre.py` : l'ASF, l'AGFF, la CET de l'Agirc, la CEG et
  la CET, ligne à ligne comme le compte, le forfait des cultes, les statuts
  exclus, et la part salariale annualisée que la fiche de paie lira. Le paquet
  porte leurs barèmes sous `contributions_equilibre`
  (`scripts/construire_donnees.py`, `_contributions_equilibre`), lus par le
  chargeur du Python ; la structure des autres clés ne bouge pas, et la
  version du paquet reste la même : la clé est lue avec un défaut vide.
- `RevalorisationServie.regimeConvenu` et `coefficientPoints`
  (`moteur/js/revalorisation.js`) : la valeur de service convenue de
  l'Agirc-Arrco, que le portage avait laissée au coût figé, bâtie à la
  première demande. Sous le simulateur du site, qui ne porte pas les
  conventions du COR, elle vaut un, comme en Python.
- `moteur/js/cycle-de-vie.js` : `Convention`, `Flux`, `Indicateurs` ; ce qui
  est versé (`cotisationsVersees`, `cotisationsReformees`,
  `cotisationsLiberales`), ce qui est servi (`niveauxActuels`, par
  `faireVivre` jusqu'à l'année courante puis la convention de la page Coût,
  `niveauxNotionnels`), `fluxDesSystemes`, `pensionsEsperees`,
  `rendementInterne`, `indicateurs`, `indicateursDesSystemes` ; `ageDeDecesCor`,
  `tauxDePrelevement` ; l'âge d'équilibre du diviseur (`ageDEquilibre`,
  `ageCible`, `diviseurA`) et l'âge de part de vie constante
  (`ageDePartDeVieConstante`, `partDeVie`, `dureeEsperee`). Les onze
  indicateurs, sous la convention de l'OCDE et sous un âge de décès fixe, en
  table unisexe ou par sexe, à tout taux d'actualisation.
- Ce qui n'est pas porté est refusé, non approché : une convention nette —
  donc celle du COR, qui lit les prélèvements de chaque année — et une
  convention après impôt lèvent une erreur qui nomme le module qui manque.
- `tests/test_cycle_de_vie_portage.py` et `tests/js/comparer-cycle-de-vie.mjs` :
  sept carrières du simulateur du site — non-cadre parti en 2010, que le droit
  a fait vivre ; cadre partie en 2020 ; non-cadre de 1962 ; cadre de 1975 à
  66 ans ; fonctionnaire de l'État ; artisan ; non-cadre de 1990 —, deux
  conventions, et les âges d'équilibre de trois générations : chaque chiffre
  se retrouve à 10⁻⁹ près, du premier coup. Le test refuse aussi ce qui n'est
  pas porté. Il tient en deux secondes : niveau rapide.
- `index.html` précharge les deux modules (`modulepreload`), comme
  `test_web.py` l'exige de tout module de `moteur/js/` ; aucune page ne les
  importe encore.

**Pourquoi l'impôt n'est pas porté d'abord.** La convention après impôt se
calcule sur le net imposable, qui suppose les revenus nets de chaque année,
donc l'histoire des prélèvements (`prelevements_historiques.py`) et la fiche
de paie de chaque année : l'impôt vient après eux, non avant. Le bloc de
l'étape 5 le dit.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les revenus nets au portage* : le jumeau de
   `donnees/prelevements_historiques.py` (la marche de chaque prélèvement, ses
   familles indépendantes, le taux des pensions de chaque année) et la clé du
   paquet qui le porte ; puis `revenusNets`, `prelevementsParAnnee`,
   `convention_cor`, `conventionNette`, et `fluxDesSystemes` avec `nets`. Le
   même test s'étend alors à la convention du COR.
2. *L'impôt au portage* (étape 5) : `impot_revenu.py` et
   `donnees/impot_revenu.py`, le barème dans le paquet, puis la convention
   après impôt.
3. *Les âges de départ* (`depart`, `balayage`, `ages_de_depart`) et les âges
   d'équilibre d'un cas type (`ages_d_equilibre`), qui demandent les cas types
   du COR en JavaScript, ou une carrière du site à leur place.
4. *L'affichage*, avec l'étape 10, par la session du site : les modules sont
   prêts à être importés par `pages.js`.
5. Puis, inchangés : la révision de 2026 et la rémunération moyenne par tête
   du COR, Typfallsmodellen au registre.
