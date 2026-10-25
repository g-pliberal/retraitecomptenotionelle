# Étape 10, sixième partie : la clôture — les cinq points du registre relus, les trimestres de chaque départ

**La demande.** Le propriétaire, le 25 octobre 2026, pour la quatorzième vague
de sessions menées sans lui : avant de clore l'étape 10, dont les cinq points
sont faits, relire les cinq points du registre encore `a_reprendre` au
chantier 138.10 — Marel, Oscar, Osiris, Nos retraites, le gain de la
suspension —, puis les « s'il le faut » des notes de l'étape. Pour chacun,
dire ce que le dépôt en fait : repris, encore à faire, ou coupé, avec sa
raison, comme la coupe du 14 octobre le permet pour le léger
(`2026-10-14-la-coupe.md`) ; le site y est son propre rang, où « aucun chiffre
ne bouge, l'usage décide ». Ce qui demande une retouche des pages se fait, le
test d'abord. Session du 25 octobre, la seule sur les pages.

**La veille.** Aucune règle du scénario 1 ne change, et le journal de veille
n'a pas d'entrée.

**Ce qui est fait.**

- La page des résultats. « Comme votre estimation officielle » dit, à chacun
  de ses départs, ses trimestres pour ceux que la génération requiert —
  « février 2032, âge légal, avec décote, 165 trimestres pour 172 requis » :
  la durée tous régimes, enfants compris, que « Mon estimation retraite »
  annonce à chaque âge, et que le lecteur compare à la sienne
  (`estimationOfficielle`, `pages.js`). Le test,
  `test_chaque_depart_dit_ses_trimestres_comme_l_estimation_officielle`
  (`tests/test_estimation_du_site.py`), vu rouge : chaque rangée dit la durée
  de son départ ; le né en mai 1968 entré à vingt-deux ans est sous la durée
  requise au plus tôt, d'où sa décote, à elle au taux plein, au-dessus au
  taux plein automatique ; la carrière longue part la durée atteinte ; la mère
  de trois enfants la passe dès l'âge légal. Le bloc est ouvert sous le
  résultat : ses dix mots de plus dépassaient de cinq la borne de ce qu'on
  traverse (`test_la_page_de_resultats_replie_son_detail`), et son chapeau
  perd ce que la table montre déjà, « que chacun consulte », « aux âges
  qu'elle chiffre ».
- Le registre, chantier 138.10 : de ses dix points, neuf sont repris, un est
  coupé, aucun n'attend. Marel, repris : les départs de l'estimation, à son
  format, chacun avec son mois, ses trimestres et son montant, chaque
  année entre eux au dépliant « Partir plus tôt ou plus tard », et tout autre
  âge en le saisissant. Oscar, repris pour la plage d'âges : le dépliant, de
  l'âge d'ouverture au taux plein automatique ; au-delà, la saisie, jusqu'à
  119 ans (action 151) ; les cas types du dépôt, de trimestre en trimestre,
  par `scripts/cycle_de_vie.py --ages` (étape 9) ; ses grilles par génération
  sont l'action 158. Osiris, repris de même, pour les générations qu'on
  nomme. Nos retraites, repris : la table sous le résultat, sous les quatre
  systèmes que le site montre — il n'en montre plus six
  (`SCENARIOS_MONTRES`) —, trois états du droit, et ce que vaut chaque âge
  de l'estimation, en mots et en trimestres ; la surcote ne s'y nomme pas,
  ce qui est léger, et coupé. Le gain de la suspension génération par
  génération (`simulateur_aurain`), coupé : la page le donne pour la
  génération saisie, au mois de naissance, et pour la carrière même ; la
  table de toutes les générations redirait les textes que les tables du
  dépôt portent ; une page qui compare les générations est l'action 143, que
  le propriétaire n'a pas lancée.

**Les restes des notes de l'étape**, chacun tranché.

- Note du 16 octobre, point 5, au dépliant des âges. La convention du COR en
  bascule, coupée : le dépliant suit celle de l'OCDE, que sa bulle dit, et
  celle du COR se lit sur les cas types (`scripts/cycle_de_vie.py --ages
  --cor`). Le pas du trimestre, coupé : les trois mois exacts de
  l'estimation sont au tableau « Comme votre estimation officielle », tout
  autre se saisit, et le pas d'un an tient le dépliant à quatre ou cinq âges.
  Les systèmes 5 et 6, nuls : le site ne les montre plus nulle part, par
  décision (`SCENARIOS_MONTRES`). La carrière saisie par la pension ou déjà
  liquidée n'a pas d'âge à balayer, comme dans l'estimation officielle : ce
  n'est pas un reste.
- Note des droits contrefactuels. Ce qu'ils ne changent pas reste déclaré
  par la bulle du dépliant, là où sont les chiffres : léger, coupé. Les deux
  tables d'âges au recoupement de l'IPP, nul, coupé : elles ne servent qu'au
  droit contrefactuel, citent leur texte mot pour mot dans leur en-tête, se
  tiennent aux textes par `tests/test_droits_contrefactuels.py`, et ce
  recoupement « ne certifie rien » (`controle_recoupement_ipp`). Le gain
  génération par génération : coupé, ci-dessus.
- Note du contrôle d'un relevé. Le contrôle des autres régimes, léger, coupé :
  sa bulle dit ce qu'il laisse de côté — la fonction publique, les régimes
  spéciaux, les indépendants, qui valident aussi par leur assiette minimale et
  ce qu'ils ont payé, que le relevé ne porte pas. L'outre-mer, léger, coupé :
  la ligne d'un relevé ne porte pas son département, mais le calcul garde ses
  trimestres ; au seuil de la métropole, plus haut de 1949 à 1951 et de 1972
  à 1995 (R. 753-21), le contrôle ne peut y trouver qu'une année qui en
  retient plus que son revenu n'en valide, que la page explique sans
  demander de la vérifier. Ce que les trimestres manquants changeraient,
  léger, coupé : la saisie le chiffre, en corrigeant les trimestres de la
  ligne (« :trimestres »).
- Note de l'indice majoré. L'indice dans le relevé et le barème du champ
  attendent les grilles, à l'étape 4 de l'action 158 : ce n'est plus
  l'étape 10.
- Note du solveur inverse. La comparaison A/B et le rapport, légers, coupés,
  comme le dit déjà le point de `simulateur_aurain` qui les porte, repris
  pour le solveur : la page Coût ne montre que la référence, à côté de ses
  variantes démographiques, et le site a sa feuille d'impression. Un solde
  moyen sur un horizon, les leviers dosés ensemble, la sous-indexation,
  l'écrêtement et le plafond, légers, coupés : le COR chiffre ses trois
  leviers chacun seul, et la page les dose de même.

**Ce que montrent les mesures.** 41 des 82 rendus de page témoins changent,
et seulement par les 82 cellules de départ qui gagnent leurs trimestres et
par le chapeau du bloc ; aucun des 909 témoins de simulation ne bouge. La
simulation témoin passe de 1 015 à 1 018 mots à traverser, pour une borne de
1 020 ; la page Simuler dépliée tient son budget ; au navigateur,
`tests/test_ecrans.py` ne trouve ni débordement, ni grand vide, ni erreur.
Au tableau de bord, le registre passe de 53 points à reprendre à 48, de 143
repris à 147, de 38 coupés à 39 ; le chantier 138.10 n'en a plus aucun.

**La limite.** Aucune : chaque reste coupé se déclare là où on le lit — au
registre, son état et sa raison ; dans les bulles des dépliants, ce que la
page laisse de côté.

**L'étape est close.** Son bloc « Reprise » est ôté de sa première note
(`2026-10-16-etape-10-ages-de-depart-au-site.md`). Au propriétaire : rien à
trancher.
