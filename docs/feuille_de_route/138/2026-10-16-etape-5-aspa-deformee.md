# Étape 5, cinquième partie : l'ASPA d'un scénario sans minimum, sur une distribution déformée

**La demande.** Le point 3 de « Ce qui reste » de
`2026-10-14-etape-5-effet-retour.md` : l'effet retour déplaçait la
distribution des pensions de l'EIR du même facteur pour tous, si bien qu'une
pension portée au minimum baissait dans un scénario sans minimum contributif
comme la moyenne ; l'ASPA en était sous-estimée.

**Ce qui est fait**, dans `src/retraite_notionnelle/effet_retour.py` :

- `_deformer` retire le minimum au bas de la distribution : la part des
  retraités dont le régime principal sert un minimum (EIR de 2020,
  `caracteristiques` : 38,5 % des femmes, 12,4 % des hommes, 26,1 % de
  l'ensemble), prise au bas, perd la part de sa pension moyenne que le
  complément moyen de l'EACR représente — 122,2 € par mois aux régimes
  alignés en 2020 (`complement_minimum`, colonne m1,
  `regimes/minimum_contributif_montant.csv`, que le modèle lit désormais :
  sorti de `HORS_DU_MODELE`). Le reste monte d'autant : la moyenne est celle
  que la grille dit. Le bas perd 27 % chez les femmes, 21 % chez les hommes.
- La déformation garde le rapport des deux sexes de la garantie (la durée non
  cotisée). Le système actuel, lui, n'est plus déformé par ce rapport : il est
  l'enquête déplacée ; il l'était jusque-là, des deux côtés de la différence.
- Un troisième taux, `EffetRetourAnnuel.aspa_deformation` : l'ASPA de plus que
  la déformation appelle à pension moyenne égale, rapportée aux pensions
  propres du scénario (`AvenirAnnuel.pensions_propres_constants`, la base
  hors réversion au rapport de la grille), et non à l'économie : rapportée à
  elle, elle valait jusqu'à 65 fois l'économie du scénario 5 en 2034, dont la
  distribution de l'EIR ne bouge presque pas quand la dépense du COR épargne
  46 milliards de réversion. `EffetRetourAnnuel.montant` additionne les deux.
- Les scénarios prospectifs servent au droit actuel, minimum compris, les
  pensions liquidées avant la bascule : la déformation n'en touche que le
  reste (`masse_stock`, la `MASSE_STOCK` de `cout.py`).

**Ce que cela donne**, sous la référence, de 2026 à 2070 : l'effet retour
reprend 27,3 % de l'économie du scénario 2 (26,8 avant), 29,3 % du 3 (27,5),
30,4 % du 4 (27,7) et 32,1 % du 5 (28,3). La déformation coûte 0,7 à 1,2 %
des pensions propres des scénarios rétroactifs, d'un bout à l'autre ; celle des
prospectifs monte de 0,03 % en 2026 à 1,2 à 1,3 % en 2070. Aucun témoin ni
chiffre ancré ne porte l'effet retour : rien d'une page ne bouge.
`tests/test_effet_retour.py` tient la moyenne gardée, le complément lu, la
déformation entre 0 et 2 % des pensions propres, et le stock des prospectifs.

**Limites**, à reporter dans `docs/limites/5-bis-cout-agrege.md` à la fin de
l'étape : les bénéficiaires du minimum sont pris au bas de la distribution,
or la moitié des hommes du premier quintile d'équivalent carrière complète
n'en a pas ; l'EIR les compte parmi tous les retraités, la distribution parmi
les résidents ; le complément est celui des nouveaux retraités du privé, que
le minimum garanti du public dépasse, rapporté à la pension moyenne des
bénéficiaires et non retiré à chacun, sans le relèvement de 2023 ; les
prélèvements restent calculés sur la distribution déplacée, non déformée.

**Ce qui reste** de l'étape, dans l'ordre : au propriétaire, si l'effet retour
entre dans le solde ; son affichage, à la session du site ; les années d'avant
2019 ; l'impôt au site, le bénéfice des indépendants, les règles d'avant 1981.
