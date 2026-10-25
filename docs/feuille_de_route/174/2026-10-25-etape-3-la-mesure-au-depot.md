# L'étape 3, la mesure au dépôt, et les intertitres des sections repliées

**Le 25 octobre 2026, la demande.** Le propriétaire : « Fait les choses qui
n'ont pas besoin de mon avis. » Ce sont les deux que la note de l'étape 2
laissait sans choix : les intertitres des sections repliées, et l'étape 3. La
session y ajoute la mesure du site en ligne, une fois l'étape 2 déployée.

**Les intertitres des sections repliées.** Sous « Pour aller plus loin », un
`<h2>`, des sections repliées s'ouvraient sur des `<h4>` : un niveau sauté pour
qui les déplie. Lighthouse ne le voyait pas, puisqu'il ne lit que la page
fermée. Deux tests le disent d'abord, rouges sur Coût, Droits non cotisés,
Méthode et les résultats. `test_aucun_titre_ne_saute_un_niveau` lit aussi la
page dépliée ; `test_une_section_repliee_s_ouvre_sur_le_niveau_sous_son_titre`
exige que le premier intertitre d'une section soit d'un niveau sous le titre
qui la précède, que la section voisine en porte ou non. Sans ce second test,
une section à `<h4>` posée après une section à `<h3>` passerait pour son
enfant. Vingt-trois intertitres de `pages.js` passent en
`<h3 class="intertitre">` : les dépenses, les scénarios, l'équilibre et les
sources du Coût, la liste et les états des Droits non cotisés, la fusion et la
fiabilité des données de la Méthode, et les trois sections des résultats.
`.dedans > h3.intertitre` rejoint la règle des `<h4>` repliés, assez faible pour
laisser au premier enfant sa marge nulle. Les 696 propriétés calculées de ces
intertitres, dépliants ouverts, à 390 et à 1 440 points, sont celles du site en
ligne. Le témoin des pages ne change que de leurs 248 balises. Restent trois
`<h4>`, chacun sous un `<h3>` : la carte « Tous les dispositifs », et les deux
de l'accueil.

**La mesure au dépôt (étape 3).** `scripts/notes_lighthouse.py` note les dix
routes de `tests/test_ecrans.py`, en mobile puis au bureau, l'une après
l'autre ; Lighthouse est tiré par `npx` à la version que le script fige,
13.5.0, hors des dépendances du dépôt. Il lit le site en ligne ; `--local` sert
l'arbre de travail compressé comme GitHub Pages, mais en HTTP/1.1, et sa
performance n'est qu'indicative. `--verifier` sort en erreur dès qu'une note
n'est pas pleine. Les rapports JSON restent sous `.cache/lighthouse/` ; le
résumé dit les cinq notes, les métriques, et les audits qui baissent une note.
Sept tests dans `tests/test_outillage.py`, écrits avant lui : les routes, égales
à celles des écrans, la commande et sa version, le relevé et le résumé d'un
rapport, les audits lancés un à un, la note pleine qu'exige `--verifier`, le
serveur compressé, le Chromium des sessions. `docs/outillage_interface.md` le
décrit, et `test_l_outillage_annonce_les_versions_qu_il_installe` y tient sa
version ; `moteur/CLAUDE.md` le nomme.

**L'étape 2, en ligne.** La suite complète de GitHub est verte sur 691d885, et
le site déployé à 23 h 33 (UTC). Le script, sur le site en ligne :

| Les dix routes | Perf. | Access. | B. P. | SEO | Agentic | FCP | LCP | CLS |
|---|---|---|---|---|---|---|---|---|
| mobile, avant | 35–59 | 97–100 | 100 | 100 | 1–100 | 6,3–6,7 s | 10,5–10,9 s | 0–1,13 |
| mobile, après | 59–60 | 100 | 100 | 100 | 100 | 6,2–6,4 s | 10,5–10,9 s | 0 |
| bureau, avant | 63–66 | 97–100 | 100 | 100 | 1–51 | 1,1–1,2 s | 1,8–1,9 s | 0,96–1,05 |
| bureau, après | 87–90 | 100 | 100 | 100 | 100 | 1,1–1,3 s | 1,8–1,9 s | 0,005 |

Ce qui baisse encore une note n'est plus que la vitesse : le FCP, le LCP et le
Speed Index des vingt mesures, et une fois le TBT, 90 ms, aux résultats sur le
bureau. Tous attendent le moteur, donc le pré-rendu (étape 4), que les choix
du propriétaire ouvrent. Les intertitres de cette note ne changent aucune note,
puisque Lighthouse ne lit pas les sections repliées.

**Fichiers.** `moteur/js/pages.js`, `moteur/style.css`, `moteur/CLAUDE.md`,
`scripts/notes_lighthouse.py`, `docs/outillage_interface.md`,
`tests/test_web.py`, `tests/test_outillage.py`, `tests/test_prose.py`, le
témoin des pages, cette note et l'action 174. Ni journal de veille : le
scénario 1 n'est pas touché.
