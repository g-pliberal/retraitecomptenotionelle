# La suite rouge du 12 novembre : le test de l'inscription n'avait pas d'identité sur le coureur de GitHub

**Le constat.** Les courses 1694 (sur e4fc26a) et 1698 (sur 45df24d) de
`tests.yml` ont fini rouges, sans verdict écrit : `main` avait bougé pendant
chacune, et `publier_fabrique.sh` ne pousse alors rien.
`.github/etat_suite.yaml` disait donc encore « vert sur 7574ea4 ». Dans la
course 1698, un seul test échouait sur 8 081 :
`tests/test_outillage.py::test_l_inscription_de_github_se_refait_quand_une_session_la_devance`,
code de sortie 128, sortie d'erreur vide.

**La cause.** Ce test, écrit à l'étape 4, fait pousser une session de poche
pendant l'inscription. Son commit se joue dans la commande que lance
`publier_inscription.sh`, donc sans l'identité du test, que `_inscrire` retire
exprès à la course. Dans un conteneur de session, git a une identité globale
et le commit passe ; sur le coureur de GitHub il n'y en a pas, git refuse, et
la commande de poche, qui tait ses sorties, s'arrête sur 128. Reproduit en
local par `HOME=/tmp/vide GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`.

**La réparation.** Le commit de la session de poche dit son identité
(`git -c user.name=… -c user.email=…`). Seul le test change : le script, qui
est une garde, n'avait pas de défaut et n'est pas touché. Vérifié : le fichier
`tests/test_outillage.py`, 73 verts avec et sans identité globale ; la suite
rapide verte.

**Ce qui reste.** Le verdict de la suite complète sur un `main` qui porte les
étapes 7 et 8 de l'action 184 et les étapes 1, 4 et 7 de l'action 192 : aucune
course ne les a encore jugées.
