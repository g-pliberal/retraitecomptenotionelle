# Consignes de `moteur/` : le portage et le site

Claude Code les charge à la première lecture d'un fichier de `moteur/`, en
plus de `CLAUDE.md`. Le dossier porte deux zones : le portage JavaScript du
modèle, jumeau du Python de `src/`, qui fait foi et se modifie le premier
(`src/CLAUDE.md`), et le site.

- **Le texte du site ne s'écrit qu'en JavaScript** : `moteur/js/pages.js`,
  `gabarit.js`, et `moteur/style.css`, sa propre source. Le Python le lit par
  `web/site.py`, qui le fait rendre par node ; les témoins de pages se refont
  par `construire_temoins.py`, après le paquet, et leur diff montre ce qu'une
  page a changé. Seules les pages dont le formulaire est le sujet le figent
  entier (`FORMULAIRE_ENTIER`) ; les autres n'en gardent que la balise.
- **L'outillage d'audit d'interface** (Impeccable, Web Interface Guidelines,
  Playwright CLI) : `.claude/skills/`, mis en place par
  `scripts/setup_ui_tools.sh` ; voir `docs/outillage_interface.md`.

## Listes de contrôle

- **Une retouche de `moteur/js/pages.js`** : le budget de mots du formulaire
  vierge (`test_le_simulateur_tient_en_peu_de_mots`) ; toute phrase en gras
  d'une page figée au catalogue `data/reference/site/affirmations.yaml`, avec
  son contrôle ; `python scripts/construire_temoins.py`, puis
  `python scripts/resumer_temoins.py` ; `python -m pytest -m site`.
- **Un champ de saisie de plus** : les deux saisies, `saisie.py` et
  `saisie.js` — la lecture, la vérification, la réécriture de l'adresse — ;
  toute borne `min` ou `max` du formulaire opposée aussi par la saisie ; les
  deux contextes ; la chronologie s'il porte un fait ; un témoin de
  simulation, et de page si la page change ; `python -m pytest -m site`.
