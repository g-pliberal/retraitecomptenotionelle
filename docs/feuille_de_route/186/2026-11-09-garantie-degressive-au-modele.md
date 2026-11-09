# La garantie vieillesse dégressive écrite au modèle, au scénario 6 seul

Le 9 novembre 2026, d'après « La consigne de la session du modèle » de
`2026-11-09-garantie-degressive.md` : les décisions 100 à 102 du programme
sont au code, le test d'abord. Rien d'autre n'est touché : ni les scénarios 1
à 5, ni le recours, ni les pages du site.

## Ce qui est écrit

**Deux paramètres** (`config.py`, `moteur/js/config.js`) :
`part_retrait_entier_garantie` et `taux_retrait_garantie`, tous deux à 0,5. À
un et un, la garantie redevient différentielle.

**Le barème, une fois par langage** : `complementGarantie`
(`moteur/js/garantie.js`), qui fait foi, et son jumeau `complement_garantie`
(`garantie.py`). Avec pivot = part × plancher : plancher − ressources jusqu'au
pivot ; au-delà, max(0, plancher − pivot − taux × (ressources − pivot)).

**Pour une carrière**, deux lecteurs, et non un : `_garantieVieillesse`
(`scenario-notionnel.js`), au départ, que la consigne nommait ; et
`pensionAujourdhui` (`revalorisation.js`), qui recalcule la garantie d'une
retraitée d'aujourd'hui et portait la même soustraction. Leurs jumeaux Python
suivent, ligne pour ligne, et refont les témoins au bit près.

**Pour le coût**, en Python seul : `_manque_moyen` (`garantie.py`) intègre le
barème sur une tranche, morceau par morceau — sous le pivot, dans la pente,
rien au-delà de la sortie. `cout_garantie`, `cout_garantie_par_sexe` et
`GarantieDistribution` (`cout.py`) reçoivent la forme ; `_garantie_distribution`
la lit aux paramètres, pour le coût comme pour le calage de la mortalité des
bénéficiaires et de la part de qui vit seul ; `_reprises_successions` la lit
au calage. La reprise ne change pas de règle : elle porte sur le complément
entier (décision 101).

**La fiche** `garantie_vieillesse.yaml` cite les trois décisions ; la limite
« La garantie est dégressive, et s'éteint au-dessus du plancher »
(`docs/limites/4-regimes-incomplets.md`), la méthodologie (« La troisième :
elle est dégressive ») et une phrase du README suivent. La sonde de prose
`garantie_complement` lit désormais le moteur : elle portait sa propre
soustraction.

## Les tests

`tests/js/garantie-degressive.test.js` et `tests/test_garantie_degressive.py`
posent à la main les valeurs de la consigne (seul : 0 → 1 050 ; 400 → 650 ;
525 → 525 ; 600 → 487,50 ; 1 124,85 → 225,08 ; 1 575 → 0 ; en couple : 0 →
800 ; 400 → 400 ; 593,19 → 303,41 ; 1 124,85 → 37,58 ; 1 200 → 0), la
monotonie, et le retour au différentiel à un et un : au bit près pour le
barème, pour le manque moyen d'une tranche (contre l'ancienne formule,
recopiée dans le test) et pour le coût de la distribution de la DREES. Les
tranches sont posées à la main elles aussi (500-600 € seul : 514,06 € en
moyenne ; 1 500-1 600 € : les trois quarts servis, 14,06 €).

Une réserve sur le bit près : la garantie d'aujourd'hui (`pensionAujourdhui`)
additionne maintenant les ressources avant de les opposer au plancher, là où
elle les en retranchait une à une ; à un et un, elle peut différer de
l'ancienne d'un dernier bit. Aucun témoin n'est à ce réglage.

Dix tests décrivaient la garantie différentielle, et sont récrits depuis la
décision : le tableau de la proposition (900 € et 900 € : 300 € et non plus
0), l'ouverture à 65 ans, les deux étages, la rente d'ici l'ouverture, la
garantie d'aujourd'hui, le pilier volontaire (repris en entier sous la moitié
du plancher, de moitié dans la pente : un test de plus), la répartition sans
le pilier, le mi-temps des mères, l'univers prospectif, la trajectoire du
coût.

## Le coût : l'étude est retrouvée

Au recours de 0,5 que le modèle porte encore, moyenne de 2026 à 2070 : versé
0,5046 point de PIB (l'étude : 0,505), net des reprises 0,3088 (0,309) ; en
2030, versé 0,586 point (0,59) et 8,671 millions d'ayants droit (8,67). Aucun
écart. `test_la_garantie_degressive_coute_ce_que_son_etude_en_disait`
(`test_cout.py`) le tient, ramené au recours de l'étude pour survivre à la
décision 20.

Et le contrôle inverse, le coût entier refait sous les deux paramètres à un :
versé puis net, 0,4603 et 0,4522 point en 2026, 0,3817 et 0,2718 en 2040,
0,3616 et 0,1718 en 2070, les six chiffres du modèle d'avant que l'étude
relevait ; en 2024, 2 800 133 bénéficiaires et 14 307,1 M€ de 2026, ceux que
le test du panorama de la DREES tenait le 5 novembre.

## Ce que le changement déplace

- **Les témoins** : 314 pensions du scénario 6 sur 932 montent, de 14,45 % en
  médiane, de 0,27 % à 32,12 % ; aucune ne baisse ; les scénarios 1 à 5 ne
  bougent pas.
- **Le coût** (fabriqué ici, que GitHub refera) : la garantie versée passe de
  14 à 19 Md€ de 2026 en 2026 comme en 2070 (0,5 → 0,6 % du PIB, 0,4 →
  0,5 %) ; son cumul passé de 1 377 à 1 523 Md€ ; en 2024, 4,28 millions de
  bénéficiaires au lieu de 2,80, pour 355 € par mois en moyenne au lieu de
  414. Au chiffrage (`docs/chiffrage_plf.md`), l'écart de solde de 2026,
  garantie comprise, passe de −2,48 à −2,63 point de PIB (−76 → −80 Md€).
- **Les cas types** : le smicard né en 1975, seul, passe de 1 129 à 1 318 €
  nets par mois, de −13,1 % à +1,4 % face au droit actuel
  (`docs/parcours_presentation.md`).
- **L'accueil** : la baisse moyenne de qui n'est pas encore à la retraite
  passe de 26 à 23 %, de 14 à 12 % s'il place les cinq points, et celle d'un
  retraité d'aujourd'hui de 28 à 25 %.

## Ce qui reste

1. **Le recours de 100 %** (décision 20), étape 3 du plan de
   `2026-11-07-reversion-scenario-6-plan.md` : il double le versé et le net.
2. **Le site** (chantier 9). Les pages disent encore la garantie
   différentielle, à `pages.js` : « différentielle » aux lignes 7917, 7982,
   13385, 15196, 15477 et 16820 ; le tableau de la proposition, que la page
   recalcule par sa propre soustraction (ligne 8073) et où « 900 € et 900 € »
   reste à 0 ; la garantie sur la distribution de la page Coût, par
   `manqueMoyen` de `moteur/js/garantie.js`, resté différentiel puisque
   seules les pages le lisent, et à porter comme `_manque_moyen`. Au
   catalogue, `cout.queue_basse` est déclarée `contredite` (action 186,
   contrôle `garantie_sert_au_dessus_du_plancher`) ; le « différentielle » de
   la portée d'`accueil.une_seule_prestation` est à récrire avec la page.
3. **Le test du panorama de la DREES** (fiche 27) : ses fenêtres sur la
   garantie de 2024 sont remesurées, la garantie différentielle gardée entre
   parenthèses.
4. **Hors de cette étape, rouge avant elle** :
   `test_chaque_chiffre_du_parcours_est_sur_sa_page` pour l'accueil (« 1 600 € »
   et « 100 % », que la page ne montre plus depuis l'étape 2 de l'action 189).
   Laissé à la session du site.
