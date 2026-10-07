# Le contexte, étape 5 : découper les gros fichiers les plus lus

**Le 7 octobre 2026, ce que chaque découpage paierait.**

- *Un module du modèle* (`cout.py`, `droit/liquider.py` 186 000 caractères,
  `scenarios/actuel.py` 156 000) : ses imports, son jumeau de `moteur/js/` si
  le portage suit le même découpage, et la mémoire des calculs, indexée sur
  `src/`, qui se refait une fois.
- *Un fichier de tests* (`test_cout.py`, `test_web.py`, `test_donnees.py`
  164 000) : son niveau dans `tests/conftest.py`, que `tests/test_niveaux.py`
  tient, et son poids dans `POIDS_REPARTI`
  (`src/retraite_notionnelle/pytest_parallele.py`).
- *Un document* (`docs/limites.md`, `docs/methodologie.md` 191 000) : son
  régime dans `data/reference/prose/zones.yaml`, ses chiffres ancrés, et la
  conservation (`python scripts/conservation.py --depuis HEAD`).
- *Un registre* (`referents.yaml`, `sources_a_explorer.yaml`) : les
  identifiants de ses entrées, que la conservation tient (`REGISTRES`, dans
  `scripts/conservation.py`), et tous ses lecteurs.

Un découpage ne rapporte que si les sessions lisaient le fichier entier, ou en
lisaient beaucoup de fenêtres : une session qui cherche puis lit par fenêtre
paie déjà peu. C'est ce que l'étape 1 tranchera.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.

**Le 7 octobre 2026, la mesure, faute du relevé du poste.** Sur la demande
du propriétaire, sans attendre le verdict de l'étape 1, comme la 4. Les
transcriptions du poste ne sont pas dans un conteneur, et l'API des sessions
du cloud rend les siennes par pages de cent événements, flux de jetons
compris : une page en porte une douzaine d'appels, pour quinze mille jetons
de contexte, et lire ainsi une seule session coûterait plus que ce qu'elle
apprendrait. La mesure retenue est celle de l'historique git, qui ne coûte
rien : un endroit qu'une session récrit, elle l'a cherché et lu.

- *Trente jours, 974 commits*, depuis le 7 septembre (le clone, superficiel,
  se creuse par `git fetch --shallow-since=2026-09-07 origin main`). Un
  commit qui ne fait, dans un document, que récrire des chiffres ancrés ne
  compte pas : `verifier_prose.py --corriger` les récrit sans que personne ne
  les lise. Ancres neutralisées, ses lignes ôtées et ajoutées sont les mêmes.
- *Ce qu'elle désigne.* `docs/limites.md`, 314 190 octets en 3 518 lignes :
  406 commits y écrivent à la main, 42 % du total, 12 864 lignes en un mois,
  plus de trois fois sa longueur. Suivent `tests/test_web.py` (178 commits),
  `docs/methodologie.md` (114), `scenarios/actuel.py` (111),
  `tests/test_donnees.py` (103), `tests/test_cout.py` (84), `cout.py` (78),
  `data/sources_a_explorer.yaml` (55), `droit/liquider.py` (36) et
  `data/reference/referents.yaml`, le plus gros (14). Seuls la feuille de
  route (534) et le README (375), de la liste de `CLAUDE.md`, s'en
  approchent ; la première tient déjà une note par fichier depuis
  l'action 148.
- *Comment on y écrit.* Peu d'endroits à la fois : deux en médiane par
  commit, 2,8 en moyenne, trois ou plus pour 30 % des commits ; les chiffres
  ancrés font le reste des retouches, jusqu'à vingt et une par commit. Et au
  même endroit d'une étape à l'autre : les étapes de l'action 147 qui y
  écrivent, de la 3 à la 14, ne le font qu'entre les lignes 3 132 et 3 335,
  dans le seul § 5 ter. Une session travaille donc dans une partie, rarement
  deux, et cherchait sa fenêtre dans 3 518 lignes, que la garde de l'étape 2
  lui interdit désormais de lire d'un coup.

**Le 7 octobre 2026, ce qui est fait.** `docs/limites.md` tient en quatorze
parties, une par section `##`, sous `docs/limites/`, nommées du numéro sous
lequel on les cite (`5-ter-trajectoire.md`, `4-regimes-incomplets.md`), et
`parametres.md`, `ecarts-au-droit-positif.md` pour les deux sections sans
numéro. Le sommaire, `docs/limites.md`, garde le titre et l'introduction,
2 544 octets : les renvois du dépôt et ceux du site, « § 5 ter des
limites », y mènent toujours, et aucun n'a été récrit. Le script du
découpage n'est pas gardé : il ne servait qu'une fois.

- *Rien n'a bougé que le rangement.* Les titres remontent d'un niveau, pour
  que chaque partie s'ouvre sur le sien ; les séparateurs de fin de partie
  tombent ; pas un mot ne change. `conservation.py --depuis HEAD` retrouve
  chaque paragraphe, et `verifier_prose.py` n'a rien à corriger.
- *Les tailles.* De 1 871 octets (§ 2) à 48 224 (§ 3) : treize parties sur
  quatorze passent sous les 50 000 de la garde ; le § 4, 61 397, se lit
  encore par fenêtres. Lire une partie d'un seul `Read` n'économise que si la
  session en a besoin entière : chercher avant de lire vaut pour les parties
  comme pour le reste.
- *L'outillage.* `zones.yaml` déclare chaque partie en état, avec les
  procès-verbaux qu'elle porte : les 32 préfixes, répartis.
  `tests/test_prose.py` exige qu'une partie neuve y soit déclarée, cherche
  les doublons dans les parties, lit le tableau du § 1 dans la sienne, et
  tient le sommaire (`test_le_sommaire_des_limites_mene_a_chaque_partie`) :
  chaque partie y a son lien, s'ouvre sur le titre qu'il annonce, et le
  sommaire ne reprend aucune section. `verifier_prose.py` compte les aveux
  `a_verifier` des parties ; deux tests de `test_web.py` y cherchent, comme
  dans le README, les comptes de tests et de régimes.
  `tableau_de_bord.py --cout` ne range plus les limites parmi les fichiers
  lourds. `CLAUDE.md`, `docs/fraicheur.md` et le § 9.3 de l'architecture
  disent le nouveau rangement, et une version le date
  (`2026-10-07-limites-par-partie.md`).
- *Ce qui reste hors de l'étape.* Le site renvoie au sommaire : ses deux
  liens au « § 5 ter des limites », dans `moteur/js/pages.js`, pourraient
  mener à la partie, à la prochaine session du site. Ce que l'étape
  rapporte, seul le relevé du poste le dira (étape 1) : combien de fenêtres
  de `limites.md` une session lisait, et combien de parties elle lit
  désormais. Les autres candidats l'attendent aussi : aucun n'approche la
  moitié de la fréquence des limites, et `tests/test_web.py`, le suivant, a
  déjà été partagé en trois.
