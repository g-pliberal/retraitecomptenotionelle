# La petite passe du site : ce que les décisions du 13 novembre retirent

*Le 14 novembre 2026, une session du site mène la part « retirer » de la
petite passe (décision 131), d'après la liste de
`2026-11-13-questions-au-proprietaire.md`.*

**Ce qui sort du site.**
- *Le tableau des rendements* (décision 127) : « Le rendement réel de vos
  cotisations, par an », dernier des quatre tableaux du dépliant « Partir
  plus tôt ou plus tard » du simulateur. La phrase d'ouverture du dépliant
  et sa bulle ne parlent plus de rendement. Le moteur calcule toujours
  `rendement_reel` : seul l'affichage part.
- *« Le rendement est le même pour tous »* (décision 128), la puce de
  l'accueil, sous « Entre deux générations ». Son entrée du catalogue passe
  aux archives (`docs/archives/affirmations.yaml`) avec sa raison, et son
  contrôle, qui ne servait qu'à elle, s'en va de `tests/test_affirmations.py`.

**Ce qui était déjà fait, ou n'a rien à retirer.**
- *« 100 % de ce que vous avez cotisé vous revient »* (décision 128) avait
  quitté l'accueil le 9 novembre (action 189, étape 2).
- *L'apport pour un premier logement* (décision 132) n'a jamais été sur le
  site : la phrase de la part capitalisée, « Ni achat de résidence
  principale, ni sortie anticipée », dit déjà le programme tel qu'il est
  redevenu.
- *« Une moindre baisse »* (décision 126) n'est écrite nulle part.

**Les tests.** `test_l_accueil_ne_dit_plus_le_rendement_le_meme_pour_tous`
(`tests/test_web.py`) et `test_plusieurs_ages_de_depart_cote_a_cote`
(`tests/test_estimation_du_site.py`), qui compte trois tableaux et aucun
rendement, vus rouges puis verts.

**Ce qui reste de la petite passe.** Une seule chose, qui ajoute au lieu de
retirer : le message aux retraités de la décision 126 — la pension nette
baisse moins que la brute, personne ne tombe sous 1 050 €, plus d'un quart
des retraités, sous ce plancher, ne perdent rien. Puis la refonte (129, 134,
111).
