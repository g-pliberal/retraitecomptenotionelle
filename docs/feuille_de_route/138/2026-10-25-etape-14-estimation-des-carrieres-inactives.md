# Étape 14, au site : le taux plein des carrières inactives dans l'estimation

**Le 25 octobre 2026 : « Mon estimation retraite » ne dit plus au taux plein,
avant l'âge d'annulation de la décote, une saisie sans activité jusqu'à son
départ à qui il manque des trimestres ; sur `main` (279a48a). La correction
est celle du pilote des cas types (63dbccd) : quand la montée du taux plein
s'arrête sans lui, la recherche reprend de l'âge d'annulation. Aucun témoin ne
bouge. En chemin : la même datation de la durée arrête trop haut la descente
vers la carrière longue d'une carrière qui ne valide plus, laissée au site.**

**La demande.** Dix-neuvième vague, le 25 octobre 2026 : une session par
tâche, que le propriétaire ne suit pas pas à pas, celle-ci seule du lot sur
les pages et sur `moteur/js/pilote.js`. Le point « au site » du paragraphe
« Hors de l'étape » de la note de la dix-neuvième partie
(`2026-10-25-etape-14-pilote-des-carrieres-inactives.md`) : `agesDeLEstimation`
date le départ « au taux plein » par un point fixe borné, et dit au taux
plein, décotée, une saisie sans activité jusqu'au départ avant l'âge où elle
l'a.

**Ce qui est fait.**

- *Le test* (`tests/test_estimation_du_site.py`,
  `test_une_carriere_qui_ne_valide_plus_n_a_le_taux_plein_qu_a_l_age_d_annulation`,
  au niveau complet du fichier). Née le 15 janvier 1966, entrée en juillet
  1983 et sans activité de 2026 à 2045, une saisie a 42 × 4 + 2 = 170
  trimestres — deux trimestres civils en 1983 —, 169 entrée en octobre, des
  172 de sa génération, qui ouvre son droit à 63 ans et 3 mois (L. 161-17-2
  et L. 161-17-3, après la suspension de la loi n° 2025-1403, article 105).
  Elle n'en gagne plus, et n'a le taux plein qu'à l'âge d'annulation de la
  décote, 67 ans pour les nés depuis 1955 (L. 351-8, 1°), où il est aussi
  automatique : l'estimation a deux départs, à l'âge légal, décoté, et à
  67 ans. Vu rouge pour cette raison : le portage la disait au taux plein à
  65 ans et 3 mois, et à 66 ans et 3 mois, en un départ à part. La naissance
  se déclare entière ; sans enfant ni mariage, aucune présomption que la garde
  décale n'y entre. Les deux saisies restent hors de `REQUETES` : sous le
  droit au 31 août 2023, leur départ au plus tôt n'est pas l'âge que le droit
  leur oppose (« Trouvé en chemin »), et le test commun des âges, qui les y
  confronterait, tomberait pour cette autre raison.
- *La correction* (`agesDeLEstimation`, `moteur/js/pilote.js`), la reprise
  du modèle : quand le point fixe du taux plein s'arrête sur un âge où le
  droit en oppose encore un plus tardif, la recherche reprend de l'âge
  d'annulation de la décote (`ageAnnulationDroit`), et en descend comme toute
  autre. `pointFixe` ne change pas, ni son jumeau, `point_fixe`.

**Ce que montrent les mesures.** Ni les témoins de simulation ni ceux des
pages ne bougent (`construire_temoins.py`, le 25 octobre), ni les départs des
requêtes de `test_estimation_du_site.py`, sous les trois états du droit. Les
deux saisies du test, sous la loi de 2023 sans la suspension (63 ans et
6 mois, 172 trimestres) : le taux plein passe aussi de 65 ans et 6 mois, et
de 66 ans et 6 mois, à 67 ans ; sous le droit au 31 août 2023, qui ne leur en
requiert que 169, elles ont leur durée, et rien ne bouge. Le balayage du
cycle de vie (`agesBalayes`), qui ne lit que l'âge au plus tôt et l'âge
automatique, ne bouge pas. La suite rapide, le filet du site, les tests
JavaScript et ceux du cycle de vie passent.

**Trouvé en chemin : la descente.** La carrière longue date sa durée cotisée
comme le taux plein date la sienne, par une soustraction signée
(`CarriereLongue.age_propose`, `scenarios/actuel.py`) : une carrière qui a
trop de trimestres l'aurait atteinte plus tôt, d'un trimestre par trimestre
de trop. Celle qui ne valide plus l'a atteinte plus tôt encore, et la
descente du point fixe, partie de l'âge que la saisie demande, s'arrête
au-dessus de l'âge où la carrière longue l'ouvre. Né le 15 janvier 1966,
entré en janvier 1982, à seize ans, et sans activité de 2025 à 2045, un
salarié a ses 172 trimestres cotisés à la fin de 2024 : le droit lui ouvre
son départ à 60 ans (`ageOuvertureDroit` de sa carrière liquidée à 60 ans),
et l'estimation le dit au plus tôt, et au taux plein, à 63 ans et 3 mois ;
qui travaille jusqu'au départ, elle le dit à 60 ans, par la carrière longue.
Sous le droit au 31 août 2023, les deux saisies du test partent de même trop
tard, à 61 ans et 3 mois et à 62 ans, quand le droit les ouvre à 60. La
correction n'y touche pas : elle ne change que le taux plein d'une montée
arrêtée, et ce que l'estimation dit d'autre devait rester. Le départ des cas
types descend par le même `point_fixe`, parti de l'âge écrit, et chaque passe
n'y descend que d'un trimestre par trimestre de trop : une carrière arrêtée
avant l'âge légal, sans trimestre de trop, resterait à l'âge écrit au lieu de
rejoindre l'âge légal où elle a le taux plein ; à vérifier au modèle.

**Ce qui ne bouge pas.** Aucune règle du scénario 1 — le pilote dit quand la
saisie part, non ce que le droit lui sert — : pas d'entrée au journal de
veille. Le bloc « Reprise » de l'étape 14, que la session de la population
tient.

**Ce qui reste**, une session par point : au site, la descente vers la
carrière longue d'une carrière qui ne valide plus (« Trouvé en chemin »),
avec son test, le salarié entré en janvier 1982 ; au modèle, la même descente
dans le départ des cas types, à vérifier.
