# Étape 18, huitième partie : la saisie des dispenses de l'assiette minimale

**La demande.** Une session du lot 3 de la vague du 17-18 octobre 2026, lancée
par l'orchestration à la demande du propriétaire (« Fait toutes les tâches qui
n'ont pas besoin de mes décisions ») : le champ de saisie des dispenses de
l'assiette minimale, que la sixième partie
(`2026-10-16-etape-18-dispenses-de-l-assiette-minimale.md`) renvoyait à la
session des pages. Le conjoint collaborateur et la Lodeom restent à d'autres
sessions.

**Le champ.** « Dispenses de l'assiette minimale » (`dispenses`), dans les
options repliées du simulateur, sous « Temps partiel », dont il prend la forme
comme la note le demandait, par année ou par plage : « 2016:2019:rsa », des
plages séparées par des virgules. Les motifs sont ceux de la table (`rsa`,
`prime_activite`, `activite_saisonniere`, `activite_non_principale`,
`pensionne`) ; la bulle les nomme avec le libellé de la table et les années où
le texte dispense, lues au paquet. Les deux saisies le lisent
(`Saisie.dispenses_analysees`, `dispensesAnalysees`) et refusent par la même
phrase une plage mal formée ou sans motif, une année hors de toute carrière,
une plage à l'envers, deux motifs pour une année ; le contexte, qui lit la
table, refuse un motif inconnu, comme celui d'une interruption. L'adresse le
garde. Un motif dit hors de ses années ne se refuse pas : la règle le laisse
sans effet.

**Où il agit.**

- *Le relevé* : chaque ligne d'emploi des années qu'il nomme en prend le motif
  (`releve_analyse`, `releveAnalyse`), une année d'interruption non ; les
  années qui prolongent le relevé jusqu'au départ aussi (`prolonger_releve`,
  `prolongerReleve`, paramètre `dispenses`).
- *Les métiers* : la chronologie coupe chaque métier, principal ou cumulé, au
  1er janvier où le motif change, comme le temps partiel coupait les seuls
  principaux (`_coupee_aux_annees`, qui remplace `_au_temps_partiel`, et son
  jumeau `coupeeAuxAnnees`) ; chaque morceau dispensé porte
  `dispense_assiette_minimale`, que `_lignes_du_parcours` et son jumeau passent
  à la ligne. Le cumulé se coupe aussi : l'activité accessoire saisonnière et
  l'activité libérale non principale sont d'ordinaire une activité ajoutée.
- *La règle* ne change pas (`dispense_assiette_minimale`, sixième partie) :
  elle ne retient le motif que pour les statuts et les années que le texte
  dispense. Toutes les activités d'une année portent le motif : l'indépendant
  qui en exercerait deux la même année, dont une seule saisonnière, les verrait
  dispensées toutes deux. La fiche `assiette_minimale_independants` le déclare,
  et le registre dit que la saisie porte les dispenses.

**Ce que montrent les mesures**, sur les trois témoins neufs, avec et sans le
champ.

- L'artisane au RSA, née le 15 mars 1962, 3 000 € par an de 1990 à 2025 sur
  son relevé, partie en avril 2027, « 2010:2027:rsa » : douze années
  dispensées, de 2016 à 2027, rien avant ; 60 trimestres au lieu de 79 ; la
  pension du scénario 1 reste 12 742 € par an, au minimum ; le compte
  notionnel prospectif, 1 476 € au lieu de 1 820 €.
- La salariée commerçante l'été, à côté, de juin 2015 à 2029,
  « 2018:2029:activite_saisonniere » : dix années dispensées, de 2020 à 2029 ;
  30 685 € au lieu de 30 690 €.
- L'infirmière libérale pensionnée d'invalidité, 1 500 € par an de 2004 à 2015
  sur son relevé, « 2004:2015:pensionne » : 53 trimestres au lieu de 63 ;
  4 005 € au lieu de 4 149 €, le prospectif 2 968 € au lieu de 3 103 €.

Aucun des 882 témoins de simulation ne bouge ; les treize pages qui figent le
formulaire gagnent le champ, et lui seul ; replié, il laisse au formulaire
vierge son budget de mots. Par une saisie de métiers, même au plus bas revenu
que le site accepte, un dixième du salaire moyen, l'infirmière libérale de 2004
à 2015, en activité cumulée, dépasse déjà le minimum de la CNAVPL : rien ne
bouge, et la dispense de D. 642-4 ne s'y voit que sur un relevé.

**Les tests.** `tests/test_saisie_des_dispenses.py` : la lecture, chaque refus,
l'adresse, le relevé et ses années prolongées, l'année dispensée qui ne valide
que ce que son revenu valide (un trimestre en 2020 pour 3 000 €, 150 heures à
10,15 € en valant 1 522,50 € ; trois sous l'assiette minimale, 11,5 % de
41 136 €), la coupe des métiers principaux et cumulés, ce que la règle retient,
et les deux moteurs confrontés, saisie, chronologie et lignes ;
`tests/test_formulaire.py` : l'aller-retour du formulaire, et la bulle, qui
nomme chaque motif du paquet avec ses années.

**Trouvé en chemin.**

- Le paquet de `main` ne portait pas la fiche `reversion_sncf`, que le commit
  `57d8328` (étape 9) a écrite sans refaire `moteur/donnees.json` : le portage
  disait la réversion de la SNCF « non portée », et `-m site` rougissait sur
  ses trois témoins. Refait ici, il ne changeait que par elle ; la session de
  l'étape 5 l'a refait sur `main` entre-temps (`902f642`), et `pousser.sh` a
  gardé le sien.
- Au modèle, non fait : l'activité exercée après le départ
  (`_lignes_apres_depart`) ne porte aucune dispense, quand D. 642-4 dispensait
  de 2004 à 2015 le libéral titulaire d'une retraite, celui-là même ; et
  `Carriere.prolongee`, qui reporte le départ à l'âge légal de la proposition,
  prolonge la Lodeom de la dernière année, mais non sa dispense. Ni l'un ni
  l'autre n'est mesuré.

**Ce qui reste**, de ce point : rien ; si le propriétaire préférait le champ
près des métiers, pour le seul indépendant, comme le menu du micro-entrepreneur,
ce serait un déplacement dans `pages.js`. De l'étape, une session par point :
les champs du conjoint collaborateur et de la Lodeom, à la session des pages ;
au fac-similé, les classes d'avant 1973.
