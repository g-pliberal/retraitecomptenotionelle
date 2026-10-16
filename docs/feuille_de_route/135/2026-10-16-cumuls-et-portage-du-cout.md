# Les cumuls tirés au hasard et le portage du coût, mesurés

**Le 16 octobre 2026.** Les soixante-sept tests qui confrontent le Python au
portage (ceux que `_confronte_au_portage` reconnaît, dans `tests/conftest.py`)
font 91 s en série, la mémoire des calculs vidée par les changements du jour :
les carrières au hasard 15 s, les étapes de l'acquisition et de la liquidation
13 s chacune, la mise en place du cycle de vie 11 s, `node --test` 8 s, les
pages au hasard 7 s, les cumuls au hasard 3,5 s ; tous les autres sous 2,5 s.
Des deux tests que la note du 10 octobre laissait à mesurer :

- *Le portage du coût n'existe plus.* Depuis le 11 octobre (action 150), le
  site ne calcule plus le coût : `contexte.cout()`, dans `moteur/js/contexte.js`,
  rend les agrégats figés de `data/derive/agregats.json`. Ce que JavaScript en
  fait encore, le lire, `test_les_deux_lecteurs_lisent_le_meme_cout`
  (`test_agregats.py`) le vérifie en 0,07 s ; le figé contre le modèle, les
  autres tests du même fichier, en Python seul. Rien à garder ni à alléger.
- *Les cumuls au hasard, gardés et allégés.* Seul test à croiser, des deux
  côtés, des statuts tirés au hasard avec une ou deux activités cumulées,
  refus compris : les autres confrontations au portage n'en jouent que
  quelques parcours fixes (`test_droit.py`, `test_chronologie.py`,
  `test_minima_agricoles.py`), et les témoins aucun. Sa moitié Python, le
  tirage et les quarante simulations, passe par `moitie_python`
  (`_cumuls_tires_au_hasard`) ; la moitié JavaScript se rejoue à chaque
  passage. 3,3 s la mémoire vide, 0,9 s pleine. Faussée à la main, la sortie
  du portage (`fiabilite` d'un parcours) le fait tomber, la mémoire pleine.

Le test reste au niveau `complet` : il ne coûte plus assez pour descendre au
`controle`, et rien d'autre ne le remplace.

**Ce qui reste**, de l'action : les pages au hasard (`test_web.py`), que la
session des pages tient ; `actions/cache` sur GitHub, que le propriétaire
décide ; les leviers 4 et 5.
