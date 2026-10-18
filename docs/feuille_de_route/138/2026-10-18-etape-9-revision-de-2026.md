# Étape 9, treizième partie : la révision de 2026 du COR, cherchée à ses séances ; elle tient aux flux, non à l'actualisation

**La demande.** Le premier reste de l'étape (bloc Reprise du 16 octobre ;
note du 10 octobre, « Ce qui reste », point 4) : la révision que le COR a
faite en 2026 du rendement interne du cas type n° 2, au-delà du passage au
net — la lire dans le document de séance qui l'a préparée, ou la demander à
son secrétariat général ; si ce sont les allègements, les porter à
`cotisations_versees` en variante de la convention du COR. Ni
Typfallsmodellen, ni la rémunération moyenne par tête du COR. Session de la
deuxième vague du 17 octobre, achevée le 18.

**Ce que disent les sources, lues le 17 octobre 2026.**

- *La séance du 16 avril 2026*, « Préparation du rapport annuel de juin
  2026 », qui a préparé le rapport : la note de présentation générale
  (document n° 1), le projet de sommaire (n° 2), la construction des
  nouveaux cas types (n° 11), le diaporama du secrétariat général. Le
  sommaire annonce de nouveaux indicateurs, « TRI du cadre du secteur privé
  et d'un salarié au Smic », et deux cas types de non-salariés, un exploitant
  agricole et un médecin ; rien n'y dit le passage au net, ni ce qui change
  au rendement du cas type n° 2.
- *Les autres séances de 2026*, du 5 février (niveau de vie), du 26 mars
  (leviers macroéconomiques), du 24 septembre (Comité de suivi, Union
  Retraite) et du 15 octobre (inégalités et pauvreté) : aucun de leurs
  documents, à leur titre, ne touche au rendement interne.
- *Le rapport*, dans sa version définitive du 9 juillet 2026
  (`RA_2026_def_1.pdf`), et le diaporama de la séance plénière de juin : les
  mêmes passages sur le rendement que la version de juin, la note 140 seule
  (« Dans les précédents rapports annuels du COR, le TRI était évalué à
  partir des rémunérations brutes »).
- *L'annexe méthodologique en ligne de 2026*, § 2.3 c et d : les cotisations
  « sans les allègements », comme le 10 octobre ; et une figure qu'aucune
  session n'avait lue, A2.13, le même rendement net actualisé selon les prix,
  de 1940 à 2000 (classeur de l'annexe, feuille « Fig A2.13 »). Celle de
  2025, figure A2.11, brute, ne publie de chiffre que sa lecture : 1,2 % pour
  la génération 2000.

**Ce que montrent les mesures** (en points de rendement ; générations 1955,
1960, 1963, 1964, 1970).

- *Sous les prix, la révision demeure.* De 1955 à 1970, le COR de 2026 baisse
  de 0,29 point sous les prix, de 0,36 sous le salaire moyen ; le dépôt, de
  0,94 et de 0,89. Dépôt moins COR, sous les prix : +0,29, +0,03, −0,13,
  −0,18, −0,36 ; sous le salaire moyen : +0,06, −0,17, −0,30, −0,34, −0,48.
  L'actualisation déplace l'écart de 0,12 à 0,23 point — les prix moins le
  salaire moyen font 0,46 à 0,53 point au COR, 0,65 à 0,69 au dépôt, dont le
  salaire moyen croît plus vite que la rémunération moyenne par tête du COR
  (+0,06 à +0,11, note du 10 octobre) — et ne fait pas la pente : sous les
  prix, communs aux deux, l'écart de pente est même plus grand, 0,65 point
  contre 0,53.
- *La génération 2000.* De 2025 à 2026, son rendement gagne 0,33 point sous
  le salaire moyen (0,50 % brut, 0,83 % net) et autant sous les prix (1,2 %
  brut, 1,53 % net) : l'écart des deux actualisations est de 0,70 point les
  deux années, la productivité du COR.
- *Ce qu'on en tire.* La révision n'est ni dans le salaire moyen qui
  actualise, ni dans une rémunération nette qui le remplacerait, comme la
  note 140 pourrait se lire : elle est dans les flux du cas type, ses
  cotisations ou ses pensions. Rien n'est porté à `cotisations_versees` : les
  allègements restent le seul candidat trouvé, pour une part seulement (note
  du 10 octobre), et l'annexe de 2026 dit encore les cotisations « sans les
  allègements ».

**Ce qui est fait.**

- *Le témoin du COR* (`scripts/fetch/cor_cycle_de_vie.py`,
  `tests/temoins/cor_cycle_de_vie.json`) lit la figure A2.13 :
  `rendement_cas_type_2_prix`, avec sa source (`source_annexe`) ;
  `lire_rendement` prend l'en-tête à la ligne des générations, que la figure
  A2.13 n'intitule pas. Le reste du témoin, relu, est inchangé.
- *Le test* `test_la_revision_de_2026_tient_aux_flux_non_a_l_actualisation` :
  la pente de 1955 à 1970 du COR et celle du dépôt, chacune la même sous les
  deux actualisations à 0,1 point ; celle du dépôt, sous les prix, plus du
  double de celle du COR ; pour la génération 2000, l'écart des deux
  actualisations le même en 2025 et en 2026, à l'arrondi de la lecture de
  2025 près (`RENDEMENT_PRIX_2000_BRUT_2025`). Vu rouge avant le témoin.
- *Le registre* (chantier 138.9) et la source du témoin (`data/sources.yaml`)
  le disent.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Typfallsmodellen*, au registre : la session suivante.
2. *La révision de 2026*, à la réponse du COR : si ce sont les allègements,
   leur histoire et leur clé d'imputation, à `cotisations_versees`, en
   variante de la convention du COR (note du 10 octobre, point 4) ; sinon,
   ce que dira la réponse. Les bornes de `REVISION_DE_2026` et
   d'`ECARTS_RENDEMENT` tombent alors.
3. Inchangés : la rémunération moyenne par tête du COR, à la session des
   données ; le rendement de −2,9 % du cadre né en 1975 sous le scénario 2.

**Au propriétaire.** La révision n'est publiée nulle part : seul le
secrétariat général du COR la sait, et le dépôt ne peut pas lui écrire. La
question à lui poser : « Entre les rapports de juin 2025 et de juin 2026, le
taux de rendement interne du cas type n° 2 a changé, au-delà du passage du
brut au net, de −0,14 point pour la génération 1955 à +0,44 pour 1970 et
+0,6 pour 2000, sous l'actualisation selon le SMPT (figure 3.7) comme selon
les prix (figure A2.13). Qu'est-ce qui a changé dans ses cotisations ou ses
pensions : les allègements généraux, déduits malgré l'annexe (§ 2.3 c) ? les
prélèvements retenus pour le net, et à quels taux chaque année ? la
carrière, l'âge de départ, la règle de liquidation ? » La réponse se verse
au dépôt, avec sa date, pour la session qui la portera.
