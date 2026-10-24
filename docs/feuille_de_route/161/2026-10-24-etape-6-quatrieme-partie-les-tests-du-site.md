# Étape 6, quatrième partie : les tests du site passent par le pont

**La demande.** La troisième vague du 24 octobre 2026 : huit sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient le point 1 de « Ce qui reste du premier lot » (note de la
deuxième partie) : les six fichiers du site — `outils_web.py`, `test_web.py`,
`test_web_saisie.py`, `test_web_revues.py`, `test_formulaire.py`,
`test_estimation_du_site.py` — portés sur le pont, les témoins identiques à
l'octet, la session de l'action 173 ayant fini.

**Les règles des deux premières parties**, appliquées telles quelles :

- ce qui éprouve la saisie elle-même — un refus, une borne, un menu,
  l'adresse qu'elle réécrit — la lit dans le portage, par `site()`
  (`saisie_du_portage`), ses constantes dans `saisie.js` ; un refus de la
  saisie s'attend par `refus_de_la_saisie`, celui que le contexte du portage
  oppose à la carrière, par `site().contexte.simuler` ou par le pont
  (`RefusDuPortage`) ;
- ce qui éprouve une règle du moteur par une saisie simule au moteur Python
  la carrière que le pont bâtit, par une fixture partagée, `saisies`
  (`outils_web.py`), assertions inchangées ; la saisie en champs de la page
  Risque s'écrit en requête, la naissance avec son jour ;
- `Montants` est la saisie : la page applique ceux du portage, que
  `montants_du_portage` (`outils_web.py`) rend, sur sa simulation ou sans
  elle ;
- le coût reste au contexte Python : la fixture `contexte` ne sert plus qu'à
  lui — le coût, les comptes, la dépense, le bilan, le paquet —, et les
  paramètres d'un réglage sont ceux que le pont rapporte, égaux à ceux de la
  saisie Python jusqu'à leur `repr`, que la mémoire des calculs lit.

**L'échelle** est celle du portage (`_echelle`). Les deux balayages de la
bascule d'unité, chaque euro des bornes, aller et retour, demandent à node
quelque cent trente-cinq mille conversions : cinq secondes chacun, la méthode
gardée sous la main. `test_web_saisie.py` passe de 42 à 48 s, en série.

**Les départs de l'estimation.** `Contexte.departs_de_l_estimation` lisait la
saisie Python. `_departs_du_pont` (`test_estimation_du_site.py`) en fait la
moitié Python sans elle : le pilote (`ages_de_l_estimation`) et la
liquidation de chaque départ (`_depart_estime`), sur la carrière que le
portage bâtit à chaque âge — la requête porte l'âge nu, à sa valeur exacte —,
et le silence du bloc tel que la saisie du portage le dit. Relevé avant
d'écrire : ses départs sont ceux d'avant, au bit près, pour les dix-huit
requêtes du fichier, sous le droit qui s'applique et sous les deux droits
contrefactuels.

**Les confrontations des deux saisies** ne gardent que ce que le portage lit :
le micro-entrepreneur — l'abattement, l'adresse, le refus —, le formulaire
renvoyé tel quel, l'exemple vierge. Les refus de la page se comparent à ceux
que le pont rapporte, mot pour mot, et chaque saisie tombe du côté que le
test lui assigne ; sur les pages tirées au hasard, le moteur Python simule
toute carrière que la page calcule.

**Un écart au dernier bit, déjà connu.** Les soixante carrières tirées au
hasard de `test_web.py` sont les mêmes qu'avant, et les mêmes six refusées ;
cinq ont, au dernier bit (8,7·10⁻¹⁶ au plus), d'autres résultats que par la
saisie Python : leur profil de salaire s'interpole (`fortement_ascendant`,
`auto`), l'écart de la troisième partie. `comparer.mjs` tolère un
milliardième, et aucun témoin n'y passe.

**Tests.** Les six fichiers, en entier : 562 ; la suite rapide, 3 032 ; le
filet du site ; `construire_temoins.py --verifier`, à jour.

**Ce qui reste du premier lot.** Le point 3, le retrait : la référence de
`test_pont.py` et de `construire_temoins.py`, et les gardes qui interdisent
la saisie Python (`test_estimation_officielle.py`, le budget de
`test_outillage.py`). Les tests du site lisent encore du contexte Python le
centre du coût, et `_depart_estime`, que la moitié Python des départs
demande : au retrait, il quitte `contexte.py` avec le pilote, ou la paire des
départs se tranche.
