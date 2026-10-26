# Consignes de `moteur/` : le portage et le site

Claude Code les charge à la première lecture d'un fichier de `moteur/`, en
plus de `CLAUDE.md`. Le dossier porte deux zones : le portage JavaScript du
modèle et le site. Chaque étape s'écrit une fois, dans le langage de
l'endroit où elle tourne (principe 4, note de décision 0003) : ce que le site
calcule chez son lecteur, ici seulement. Une étape qui a encore son jumeau
Python le suit : le Python fait foi et se modifie le premier
(`src/CLAUDE.md`), jusqu'au retrait de la paire (action 161,
`python scripts/jumeaux.py <nom>`). Le portage ne copie que ce que le
simulateur calcule, une carrière : le coût n'y est pas, et Coût, Carrières
types et Droits non cotisés lisent ce que le Python en a fabriqué
(`agregats.js`, `docs/architecture.md`, § 7.1).

- **Une adresse par page** (action 174, note de décision 0004) : l'accueil est
  la racine du site, `index.html` ; chaque autre page est un dossier de son
  nom, qui porte son `index.html` (`cout/`, `simuler/`…). Le lecteur, sa
  carrière et ses réglages, est derrière le `#`, et un mot sans `=` y désigne
  une section. `moteur/js/adresses.js` lit les deux formes d'adresse, l'ancienne
  (`#/cout?indexation=prix`) comprise, et écrit la nouvelle ; le gabarit écrit
  chaque lien relatif à la page rendue (`lien`, `route`, `versLaPage`), et le
  routeur redirige les anciennes adresses. `index.html` est la source des huit
  pages en dossier, que `scripts/construire_pages.py` fabrique (`regenerer.py`
  les refait, `.gitattributes` les déclare fabriquées) : on retouche
  `index.html`, jamais une page de dossier.
- **Les exponentielles du moteur passent par `libm.js`** : `exp`, `log` et
  `pow`, au bit près de la libm de Linux, dont le Python tient les siennes ;
  jamais `Math.exp`, `Math.log` ni `**`, qui rendraient celles du navigateur,
  et les témoins cesseraient d'être identiques (`tests/test_libm.py`). Seuls
  la présentation et le relevé lu gardent celles du navigateur.
- **Le texte du site ne s'écrit qu'en JavaScript** : `moteur/js/pages.js`,
  `gabarit.js`, et `moteur/style.css`, sa propre source. Le Python le lit par
  `web/site.py`, qui le fait rendre par node ; les témoins de pages se refont
  par `construire_temoins.py`, après le paquet, et leur diff montre ce qu'une
  page a changé. Seules les pages dont le formulaire est le sujet le figent
  entier (`FORMULAIRE_ENTIER`) ; les autres n'en gardent que la balise.
- **Les mesures que l'accueil cite** (`MESURES_BLOCAGES`, dans `pages.js`) ne
  s'écrivent pas à la main : `scripts/mesures_accueil.py` les refait comme
  leurs tests, et GitHub les récrit à chaque fabrique (action 163). Une mesure
  de plus s'y déclare, avec sa précision et son calcul.
- **Ce qu'un écran montre se vérifie dans un vrai navigateur** :
  `tests/test_ecrans.py` pilote Chromium à plusieurs largeurs, du plus petit
  téléphone au bureau — rien ne déborde ni ne défile en largeur, une légende
  touche son tracé, les quatre systèmes du simulateur tiennent dans un écran,
  aucun grand vide (action 173). Un graphique se dessine à la largeur de la
  colonne, que `rendre` reçoit et pose au gabarit (`g.poserEcran`) ; les
  témoins sont rendus au large. Un tableau trop large ne défile pas : il se
  replie (`plierLesTableaux`, dans `moteur/js/routeur.js`).
- **L'outillage d'audit d'interface** (Impeccable, Web Interface Guidelines,
  Playwright CLI) : `.claude/skills/`, mis en place par
  `scripts/setup_ui_tools.sh` ; les notes Lighthouse des dix routes, par
  `python scripts/notes_lighthouse.py` (`--local` pour l'arbre de travail) ;
  voir `docs/outillage_interface.md`.

## Listes de contrôle

- **Une retouche de `moteur/js/pages.js`** : d'abord le test de ce que la
  page doit montrer de neuf, vu rouge (`tests/test_web.py` et ses deux
  voisins) ; le budget de mots du formulaire vierge
  (`test_le_simulateur_tient_en_peu_de_mots`) ; toute phrase en gras d'une
  page figée au catalogue `data/reference/site/affirmations.yaml`, avec son
  contrôle ; `python scripts/construire_temoins.py`, puis
  `python scripts/resumer_temoins.py` ; `python -m pytest -m site`, qui joue
  aussi le site dans le navigateur.
- **Une retouche de `moteur/style.css` ou d'un dessin du gabarit** : d'abord
  la mesure qui dit ce qui doit changer, vue rouge, dans
  `tests/test_ecrans.py` ; puis `python -m pytest tests/test_ecrans.py`.
- **Un champ de saisie de plus** : d'abord le test qui le lit et le vérifie,
  vu rouge ; la saisie, `saisie.js`, seule depuis l'action 161 — la lecture,
  la vérification, la réécriture de l'adresse — ; toute borne `min` ou `max` du
  formulaire opposée aussi par la saisie ; le contexte du portage
  (`contexte.js`), seul à bâtir la carrière depuis l'action 161 ; la
  chronologie s'il porte un fait ; un témoin de simulation, et de page si la
  page change ; `python -m pytest -m site`.
- **Un chiffre de plus sur une page qui agrège** : d'abord son test, vu
  rouge, dans `tests/test_agregats.py` ; il se fabrique en Python, dans
  `_agregats` (`scripts/construire_donnees.py`) et `donnees/agregats.py`, se
  lit par l'accesseur jumeau de `agregats.js`, sans rien calculer qu'une
  règle décide, et la version du paquet monte des deux côtés (`VERSION`,
  `VERSION_PAQUET`) ; son test au vert, puis la liste d'une retouche de
  `pages.js`.
