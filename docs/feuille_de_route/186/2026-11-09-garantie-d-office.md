# La garantie servie d'office, et l'ASPA de l'effet retour à son propre taux

Le 9 novembre 2026, à la demande du propriétaire (« fait le reste »), après
la garantie dégressive (`2026-11-09-garantie-degressive-au-modele.md`) :
l'étape 3 du plan de `2026-11-07-reversion-scenario-6-plan.md`, la décision
20 du programme, « La garantie vieillesse est servie d'office ».

## Un défaut corrigé d'abord

L'effet retour chiffre l'ASPA des scénarios 2 à 5 sur une copie du calage de
la garantie (`EffetRetour._aspa`). Depuis le commit de la garantie
dégressive, cette copie en portait la forme : l'ASPA, qui se réduit « à due
concurrence », y était retirée de moitié au-delà du pivot, 87,7 € par tête au
lieu de 70,9 € au cas du test. Resté dix minutes sur `main`, corrigé par
le test qui le reproduit
(`test_l_aspa_de_l_effet_retour_reste_differentielle`) : l'ASPA ne prend plus
du calage que la population et ses mélanges.

## Ce qui est écrit

- `taux_recours_garantie` passe de 0,5 à 1 (`config.py`, `config.js`) : le
  coût compte tous les ayants droit. Un demi reste un réglage.
- Un paramètre de plus, `taux_recours_aspa`, à 0,5 : l'ASPA de l'effet retour
  se demande toujours, et garde le non-recours que la DREES mesure. Elle
  lisait le taux de la garantie tant que les deux valaient un demi.
- Le texte qui dit le recours, à `pages.js` : « Servie d'office, à tous les
  ayants droit », la note sur le non-recours de l'ASPA, et le paragraphe du
  programme. Les trois entrées du catalogue gardent leur identifiant, sous le
  contrôle `garantie_servie_d_office`.
- La fiche cite la décision 20 ; le README, la méthodologie et deux limites
  suivent ; `scripts/garantie_par_sexe.py` dit « servie d'office ».

## Ce que le changement déplace

Tout ce que la garantie coûte double, les ayants droit ne bougent pas. Versé,
en moyenne de 2026 à 2070 : 1,009 point de PIB, 0,618 net des reprises —
l'étude disait 1,01 et 0,62. En 2026, 37 Md€ au lieu de 19 (1,2 % du PIB) ;
38 Md€ en 2070 ; 8,5 millions de bénéficiaires en 2026. Le cumul passé de la
garantie passe de 1 523 à 3 046 Md€. Au chiffrage, l'écart de solde de 2026,
garantie comprise, passe de −2,63 à −3,22 point de PIB (−80 → −99 Md€), et
la dépense publique retirée de −3,24 à −2,65 point. Les témoins de simulation
ne bougent pas : une carrière ne connaît pas ce taux.

Le test du panorama de la DREES (fiche 27) est remesuré une seconde fois, aux
deux jeux de présomptions ; son test du recours (fiche 28) dit maintenant que
l'écart des têtes aux euros ne porte plus que sur l'ASPA de l'effet retour.

## Ce qui reste, et une question

- **Peut-on refuser la garantie ?** La page du programme disait « Elle se
  demande, comme l'ASPA, et se refuse : personne ne se voit imposer une
  dette ». La décision 20 ne dit que « D'office ». Le texte garde la faculté
  d'y renoncer (« servie d'office, sans demande, et elle se refuse ») ; le
  coût compte tout le monde, ce qui en fait une borne haute. Au propriétaire
  de dire si le refus reste.
- « Puis, si le propriétaire le veut, la garantie qui voit la réversion
  gardée » (même étape du plan) : non fait, non demandé.
- Le site sur la garantie dégressive : la note suivante.
