# Étape 9, douzième partie : les âges de départ au portage des indicateurs de cycle de vie

**La demande.** Le premier reste de l'étape (note
`2026-10-16-etape-9-impot-au-portage.md`, point 1) : les indicateurs de cycle
de vie à chaque âge de départ en JavaScript (`moteur/js/cycle-de-vie.js`),
rejoués contre le Python (`cycle_de_vie.py`). Ni l'affichage, ni la révision
de 2026 du COR, ni Typfallsmodellen. Session du 16 octobre, une parmi treize.

**Ce qui est fait.**

- `cycle_de_vie.py` sépare le balayage du cas type : `ages_balayes(simulateur,
  batir, age_demande, pas)` et `balayage_d_une_carriere(…)` balaient la
  carrière que `batir(age)` rend liquidée à `age`, partis de l'âge demandé ;
  `ages_de_depart` et `balayage` les appellent avec la carrière du cas type,
  sans rien changer de ce qu'ils rendent. Le portage n'a pas les cas types du
  COR : il balaie la carrière d'une saisie, comme `departsDeLEstimation`.
- `moteur/js/cycle-de-vie.js` : `PAS_DES_AGES`, `minimumVieillesse` (les deux
  étages jusqu'en 2006, l'ASPA ensuite), `derniereAnneePleine`,
  `RemplacementNet` et `remplacementNet` (les trois unités de TRAJECTOiRE),
  `Depart` et `depart` (nette ou après impôt, sous l'OCDE ou le COR),
  `agesBalayes` (sur `agesDeLEstimation`, `pilote.js`) et
  `balayageDUneCarriere`. Le calcul du taux de remplacement après impôt, sous
  une convention donnée, devient `remplacementApresImpotDe`, le jumeau de
  `_remplacement_apres_impot`.
- `tests/test_cycle_de_vie_portage.py` : trois balayages, chacun comparé âge
  par âge, chaque champ de `Depart`, à 10⁻⁹ près — une carrière longue de
  1966 après impôt, au trimestre, de 61 à 67 ans (vingt-cinq âges) ; une
  fonctionnaire de 1944 sous le COR, de 60 à 65 ans, dont les départs
  traversent 2007 et le minimum vieillesse à deux étages ; un artisan
  de 1975. Un minimum vieillesse faussé d'un millième fait échouer les trois.
  Le fichier reste au niveau rapide (dix secondes).

**Ce que montrent les mesures.** Les vingt-cinq âges de la carrière longue,
après impôt, coûtent moins d'une seconde dans node.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'affichage*, avec l'étape 10, par la session du site : `pages.js` peut
   balayer la carrière d'une saisie par `balayageDUneCarriere`, avec le
   `batir` de `departsDeLEstimation` (`contexte.js`).
2. La révision de 2026 et la rémunération moyenne par tête du COR,
   Typfallsmodellen au registre.
3. Inchangé : le rendement de −2,9 % du cadre né en 1975 sous le scénario 2,
   à regarder par une session du modèle (note de l'impôt au portage).
4. Les âges d'équilibre d'un cas type (`ages_d_equilibre`) restent au
   Python, avec les cas types ; le portage a ceux d'une génération.
