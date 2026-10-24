# Étape 6, troisième partie : le centre du coût, ce que ses tests lisaient de la saisie Python passé au pont

**La demande.** La deuxième vague du 24 octobre 2026 : neuf sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient le point 2 de « Ce qui reste du premier lot » (note de la
deuxième partie) : le centre du coût — `test_agregats.py`,
`test_bilan_compte.py`, `test_cout.py`, `test_affirmations.py`,
`test_outillage.py` — porté sur le pont, les témoins identiques à l'octet.

**Ce qui lisait la saisie.** Deux fichiers sur cinq. Les trois autres ne
lisent du contexte Python que le centre du coût — le simulateur des réglages
de référence, le coût, les avantages, les bilans, la population, la dépense —,
qui reste en Python : rien à porter. `test_agregats.py`, `test_bilan_compte.py`
et le coût du contexte de `test_outillage.py` le suivront au retrait,
`contexte.py` réduit à lui, ou un module à lui.

**Les exemples figés** (`test_cout.py`). La table se compare à ce que le
portage simule de leur saisie en champs, par `pont.saisies`, comme la
fabrique les fige ; la confrontation du portage au moteur Python, pour une
saisie, reste à `test_pont.py`. Le fichier ne lit plus ni le contexte ni la
saisie Python.

**Les affirmations** (`test_affirmations.py`). Le modèle des contrôles
simule par le pont (`Saisies`) : le portage bâtit la carrière d'une requête,
le moteur Python la simule, assertions inchangées. Ses treize saisies en
champs s'écrivent en requêtes, la naissance avec son jour (`1975-01-01`),
que la saisie présumerait sinon au 15. Relevé avant d'écrire, sur les
38 saisies distinctes que ses contrôles simulent : la carrière et les
paramètres du pont sont ceux de la saisie Python — les âges écrits en entiers
y deviennent des flottants, aux mêmes valeurs —, sauf deux, ci-dessous. Ce
qui éprouve la saisie elle-même passe au portage, par `site()` : l'inversion
d'une pension, le refus d'une saisie hors bornes, l'échelle, les défauts et
les menus. Le coût et les données qu'agrègent les pages restent au contexte.

**Un écart des deux moteurs, au dernier bit.** L'interpolation du profil de
salaire s'écrit `(haut - bas) * (age - age_bas) / (age_haut - age_bas)` en
Python (`_interpole_tranches`, `carriere.py:2962`), et
`(haut - bas) * ((age - ageBas) / (ageHaut - ageBas))` dans le portage
(`interpoleTranches`, `carriere.js:2701`) : à 31 ans en 1993, le profil d'un
fonctionnaire de l'État vaut 0,7443485023930831 d'un côté, …833 de l'autre,
et une ligne de revenu de deux carrières de fonctionnaire de l'État diffère
d'autant (14 830,709268972107 et …11). Aucun témoin n'y passe — les 889
carrières du pont sont celles de la saisie Python —, ni aucune case de la
grille des agrégats, que `test_agregats.py` compare au bit près ; aucun
contrôle des affirmations n'en dépend. Rien n'est corrigé ici : la paire de
la carrière se tranche à sa relecture, et le Python y fait foi tant qu'elle a
deux jumeaux.

**Tests.** `test_affirmations.py`, 641 ; l'exemple figé de `test_cout.py` ;
la suite rapide ; ceux de la zone.

**Ce qui reste du premier lot.** Le point 1, le site : six fichiers, après la
session de l'action 173. Le point 3, le retrait : la référence de
`test_pont.py`, et les gardes qui interdisent la saisie Python
(`test_estimation_officielle.py`, le budget de `test_outillage.py`).
