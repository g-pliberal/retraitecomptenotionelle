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
- **L'outillage d'audit d'interface** (Impeccable, Web Interface Guidelines,
  Playwright CLI) : `.claude/skills/`, mis en place par
  `scripts/setup_ui_tools.sh` ; voir `docs/outillage_interface.md`.

## Listes de contrôle

- **Une retouche de `moteur/js/pages.js`** : d'abord le test de ce que la
  page doit montrer de neuf, vu rouge (`tests/test_web.py` et ses deux
  voisins) ; le budget de mots du formulaire vierge
  (`test_le_simulateur_tient_en_peu_de_mots`) ; toute phrase en gras d'une
  page figée au catalogue `data/reference/site/affirmations.yaml`, avec son
  contrôle ; `python scripts/construire_temoins.py`, puis
  `python scripts/resumer_temoins.py` ; `python -m pytest -m site`.
- **Un champ de saisie de plus** : d'abord le test qui le lit et le vérifie,
  vu rouge ; les deux saisies, `saisie.py` et `saisie.js` — la lecture, la
  vérification, la réécriture de l'adresse — ; toute borne `min` ou `max` du
  formulaire opposée aussi par la saisie ; les deux contextes ; la
  chronologie s'il porte un fait ; un témoin de simulation, et de page si la
  page change ; `python -m pytest -m site`.
- **Un chiffre de plus sur une page qui agrège** : d'abord son test, vu
  rouge, dans `tests/test_agregats.py` ; il se fabrique en Python, dans
  `_agregats` (`scripts/construire_donnees.py`) et `donnees/agregats.py`, se
  lit par l'accesseur jumeau de `agregats.js`, sans rien calculer qu'une
  règle décide, et la version du paquet monte des deux côtés (`VERSION`,
  `VERSION_PAQUET`) ; son test au vert, puis la liste d'une retouche de
  `pages.js`.
