# Version du 31 octobre 2026 : le JavaScript fait foi

La dernière phrase du principe 4 change, sur la décision du propriétaire du
31 octobre 2026 (note de décision 0005, action 161) : tant qu'une étape du
moteur garde ses deux jumeaux, le JavaScript fait foi pour elle, et le Python
le suit, au bit près. Une règle s'écrit d'abord dans `moteur/js/`, avec son
test tiré de la source ; son jumeau Python la suit dans le même commit, et la
concordance des témoins en est le test, que `tests/js/moteur.test.js` exige
désormais au bit près sous Linux x86_64, où GitHub fabrique les témoins. Le
Python ne cesse de suivre qu'au retrait de sa paire : les témoins se simulent
encore à son moteur, et le coût bâtit et date ses carrières par lui. Le § 7.1
le dit, avec le retrait par paire ou par sous-ensemble cohérent de paires,
que reprend la table « Où va quoi » ; la table des agrégats se fabrique par
les écrivains du Python et se lit par `moteur/js/agregats.js`, les lecteurs
du Python, qui ne servent qu'aux tests, s'en allant. La carte du dépôt, les
consignes de `src/` et de `moteur/` et cinq en-têtes du portage suivent.
