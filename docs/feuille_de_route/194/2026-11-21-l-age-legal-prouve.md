# Action 194 : l'âge légal, cinq parties prouvées

Le 21 novembre 2026 (grille du 20). Aucun résultat n'a bougé : le simulateur
rend les 100 valeurs posées depuis le texte.

## Ce qui est fait

**Cinq grilles indépendantes**, `data/reference/preuves/grille_age_legal_*.yaml`,
une par version lue de la fiche `age_legal_par_generation` : `soixante_ans`
(7 cas), `loi_de_2010` (17), `loi_de_2011` (17), `loi_de_2023` (29),
`suspension_de_2025` (30). La carte les dit prouvées : les trois dernières
avec témoin (exemples des circulaires Cnav 2012/27 et 2026-07, fiches
service-public), les deux premières au texte seul. Elles sont au cliquet.

**Une grandeur de plus**, `age_legal_a_l_effet` : l'âge que la rédaction de la
date d'effet oppose à la pension, que l'assuré l'ait atteint ou non
(`ouvrir.age_legal_a_l_effet` au pont, `AgesOuverture.aLEffet`). Sans elle, 31
cas ne se rejouaient pas : `age_ouverture` est l'âge de la personne, sous la
version où son droit s'ouvre. Les cas où l'âge est atteint à la date d'effet
comparent aussi `age_ouverture` et `date_age_legal`.

## Comment la grille s'est faite

Une session séparée (Fable 5.2) a reçu dix rédactions tirées de l'index LEGI
du 16 novembre 2026 — R. 351-2 (deux), L. 161-17-2 (cinq), D. 161-2-1-9
(trois) —, 89 couples naissance, date d'effet, et une consigne : ne rien lire
d'autre, ni dépôt ni web, et dire ses doutes au lieu de s'appuyer sur sa
mémoire. Elle a retrouvé seule quelle rédaction vaut à quelle date, et que la
loi de 2025 l'emporte sur D. 161-2-1-9 resté à 63 ans pour les nés en 1964. Elle
a proposé onze cas de plus sur les seuils non couverts, entrés avec ses
valeurs. Ses fichiers sont gardés dans le dossier du projet,
`justesse/2026-11-20-age-legal-cinq-parties-prouvees/aveugle/`.

## Jusqu'où l'indépendance a tenu

- Les 89 premiers cas et le choix des dix rédactions viennent de la session
  qui connaît le code et la fiche : une rédaction que la fiche ignore manquerait
  aussi à la grille.
- Rien n'empêchait la session indépendante d'ouvrir le dépôt : elle déclare ne
  pas l'avoir fait, et cite les seuls fichiers reçus.
- Six cas (nés de 1952 à 1955, effet d'août à décembre 2011) reposent sur une
  lecture que le texte fourni ne tranche pas : la loi et le décret de fin 2011
  n'ont pas de disposition d'application dans LEGI. Aucun de ces assurés ne
  pouvait partir à ces dates.
- Quatorze dates tombent sur un quantième absent (né un 31) : seul le mois se
  compare, le même dans les deux lectures.
- La version d'avant 1985 est supposée : non prouvable sans les textes d'avant
  le code de 1985.

## Par quoi continuer

Les règles centrales du régime général — `duree_requise_par_generation`,
`decote_regime_general`, `surcote_regime_general`, `taux_plein_et_proratisation`,
`majoration_dix_pour_cent`, `date_effet_mois_suivant` — ne sont pas découpées
en versions : la carte n'en fait qu'une partie chacune, qu'aucune grille ne
prouve. Les découper, puis faire leur grille de la même façon. Le salaire
annuel moyen et le minimum contributif sont découpés mais se disent approchés :
lever ou situer l'approximation d'abord.

## La suite rouge du 21 novembre, réparée

La première publication (d4a9b7a) a fait tomber la suite complète : GitHub
refait le témoin du droit à neuf en relançant les seuls fichiers qui nomment
`droit_et_fige`, et `tests/test_justesse.py`, qui rejoue ses preuves par
`_confronter` de `tests/test_oracle.py`, n'en était pas. Les demandes des
grilles sortaient du témoin. `fichiers_qui_appellent_le_droit` relance
désormais aussi les fichiers qui importent de `test_oracle`, et un test le tient.
