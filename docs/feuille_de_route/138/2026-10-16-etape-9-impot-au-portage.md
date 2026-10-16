# Étape 9, onzième partie : l'impôt sur le revenu au portage des indicateurs de cycle de vie

**La demande.** Le premier reste de l'étape (bloc « Reprise » du 14 octobre,
note `2026-10-14-etape-9-revenus-nets-au-portage.md`, point 1) : l'impôt sur
le revenu dans le portage JavaScript des indicateurs de cycle de vie, rejoué
contre le Python (`impot_revenu.py`, `cycle_de_vie.py`). Ni les âges de
départ, ni l'affichage, ni les autres restes de l'étape 5. Session du
16 octobre, une parmi quatorze.

**Ce qui est fait.**

- `moteur/js/impot-revenu.js`, le jumeau de `impot_revenu.py` et de
  `donnees/impot_revenu.py` : les barèmes marche par marche, lus ou projetés
  sur les prix ou le salaire moyen (`BaremesImpotRevenu`, `parametres`,
  `chronique`, `croissanceMacro`) ; l'impôt d'un foyer étape par étape
  (`impotDuFoyer`, `impotAuxParametres`, `impotDUnRevenuImposable`) — les
  abattements de 10 et de 20 %, celui des personnes âgées, les parts, le
  plafonnement et ses réductions complémentaires, la décote de chaque époque,
  les majorations et minorations des années 1960 à 1992, les mesures de 2001,
  2008 et 2013, la réduction de 2016 à 2019, la prime pour l'emploi, le seuil
  de recouvrement —, en francs pour une année en francs, avec les arrondis du
  code. Le `round(x, 6)` du Python s'écrit `toFixed(6)` ; les deux ne
  diffèrent qu'à une moitié exacte du septième chiffre, qu'aucun arrondi à
  l'unité ne voit.
- Le paquet porte les barèmes sous `impot_revenu`
  (`scripts/construire_donnees.py`, `_impot_revenu`), sans leurs clés de
  source autres que l'année : 53 kilo-octets. La clé se lit avec un défaut,
  comme `prelevements_historiques` : la version du paquet ne bouge pas.
- `moteur/js/cycle-de-vie.js` : `Convention` prend l'impôt, et le refuse sans
  prélèvements ou d'une indexation inconnue ; `ImpotDeLAnnee` ;
  `Flux.impotDeLaPension` et les quatre champs de l'impôt ;
  `foyerDeLAnnee`, `anneesHorsImpot`, `impotsParAnnee`, `avecLImpot`,
  `dernierRevenuApresImpot`, `conventionApresImpot`, `pensionAuDepart`,
  `remplacementApresImpot` ; `fluxDesSystemes(…, {impot})` lit le net et
  l'imposable d'une seule fiche par ligne ; `pensionsEsperees` et
  `indicateurs` retirent l'impôt de chaque année. Plus rien n'est refusé
  hors des âges de départ, que le portage n'a pas.
- `tests/test_cycle_de_vie_portage.py` : les sept carrières sous deux
  conventions de plus, après impôt du dépôt (barème sur les prix) et du COR
  (sur le salaire moyen) ; l'impôt de chaque année du scénario 1, ses revenus
  après impôt, le taux de remplacement après impôt au départ de trois
  systèmes ; et la grille du module seul — huit foyers (salarié, retraité,
  année du départ, couple avec enfants, parent isolé avec un enfant invalide,
  veuf, invalide, couple mono-emploi), vingt-six années de 1962 à 2045, dont
  deux projetées, quatre revenus, 1975 en francs aussi : 864 impôts, chaque
  étape comparée. Tout se retrouve à 10⁻⁹ près ; la grille fait jouer chaque
  correction au moins une fois, et une décote faussée d'un centième y fait
  142 écarts. Le fichier reste au niveau rapide (six secondes).
- `index.html` précharge le module, comme `test_web.py` l'exige.

**Ce que montrent les mesures.** Le salarié au salaire moyen né en 1980,
parti à 64 ans, retrouve en JavaScript son taux de remplacement après impôt
de 72,7 % (note de l'étape 5 du 13 octobre). Les indicateurs après impôt des
six systèmes coûtent 20 à 30 ms à une carrière dans node, contre 40 ms la
première convention nette, qui charge l'histoire.

**En chemin.** Le cadre né en 1975 a, sous le scénario 2 (rétroactif), un
taux de récupération de 0,32 et un rendement réel de −2,9 %, que l'impôt ne
déplace pas : sa pension n'en paie aucun. Les deux moteurs le disent, et ce
n'est pas de cette étape ; à regarder par une session du modèle.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les âges de départ* (`depart`, `balayage`, `ages_de_depart`) et les âges
   d'équilibre d'un cas type, qui demandent les cas types du COR en
   JavaScript, ou une carrière du site à leur place.
2. *L'affichage*, avec l'étape 10, par la session du site : `pages.js` peut
   importer `conventionApresImpot`, `indicateursDesSystemes` et
   `remplacementApresImpot` ; l'étape 5 y ajoutera « l'impôt au site », le
   net après impôt de la page du simulateur, dont le module est désormais là.
3. Puis, inchangés : la révision de 2026 et la rémunération moyenne par tête du
   COR, Typfallsmodellen au registre.
