# Les étapes seules à la façade : ouvrir, liquider chaque régime et compléter servis par le portage, le contexte d'une liquidation transmis par ses neutralisations

Treizième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-foyer-a-la-facade.md`, « Ce qui reste », 1. Aucune règle,
aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Les trois étapes.** `ouvrir.ouvrir`, `liquider.liquider_chaque_regime` et
`completer.completer` passent par la façade. Chacune reçoit le relevé et ce
que la précédente a écrit, objets du moteur que le pont ne passe pas : chaque
étape de la façade (`facade.Etape`) garde donc son relevé et la chaîne des
étapes dont elle vient, options comprises. Le portage refait le relevé de la
carrière, sous ses drapeaux, puis chaque étape de la chaîne, par une entrée
neuve, `droit.etapes` (`pont.mjs`), que `pont.py` lit strictement
(`etape_de_la_liquidation_des_donnees`) : l'ouverture, `requis`, `age`,
`motif`, `trimestres_cotises` ; les pensions, `regimes` et `taux` ; les
compléments, `regimes` et `total` ; chacune, `donnees()`.

**Le contexte.** Le contexte d'une liquidation passe par ses neutralisations,
aux trois étapes et au foyer (`pont.ContexteDuMoteur`, la marque `contexte`
de `argumentDeLaFacade`), sur le moteur de l'étape. Sont refusés : le
contexte d'un autre moteur, une date d'observation, une hypothèse ; une
ouverture ou des pensions d'un autre relevé ; à `completer`, des pensions
servies, provisoires ou nationales, une autre nature, une première retraite.

**`test_liquidation.py`.** Le test « chaque étape suit son schéma » passe à
la façade, inchangé hors de sa marque : il en garde 10 marqués sur 22
(`RESTES`).

## Ce qui est mesuré

**Contre le jumeau.** Cinq carrières (salarié, agent de la SNCF, artisan
d'avant 1973, fonctionnaire mère de trois enfants, mère sous l'AVPF), sans
contexte et sous quatre, chaque étape et le foyer : les mêmes données, les
mêmes taux, pensions et totaux, au bit près, sous la référence et sous les
conventions du COR (`tests/test_facade_jumeau.py`).

**Les tests.** Trois tests neufs dans `tests/test_facade.py`, vus rouges : le
salarié né en 1960 parti à 62 ans, 156 trimestres pour 167, liquide à
43,125 %, et à 50 % la décote neutralisée ; le foyer neutralisé ne sert pas
l'ASPA. `-m rapide`, `test_facade.py`, `test_facade_jumeau.py`,
`test_liquidation.py`, `test_droit.py`, `test_reversion.py`, `test_pont.py`,
`test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. Le reste de `test_liquidation.py` attend la liste des fonctions gardées
   des deux côtés : le journal (trois tests), l'échéancier (deux), le pilote
   (trois), `faire_vivre`, et la confrontation des deux moteurs, qui part
   avec le moteur Python.
2. Puis, de « Ce qui reste » de `2026-11-15-la-liquidation-a-la-facade.md`,
   2 : `test_cultes.py`, `test_bonifications_emplois.py` et les autres
   fichiers qui lisent le relevé ; `completer.points_rco_de_chef` ; les 37
   tests marqués de `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
