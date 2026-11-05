# Le hook d'Impeccable retiré : le détecteur à la demande

**Le 5 novembre 2026.** Le propriétaire demandait si la compétence Impeccable
servait vraiment. Son hook tournait après chaque `Edit`/`Write` et à chaque
fin de tour, dans toutes les sessions, celles du modèle et des données
comprises, qui ne touchent jamais au site. Mesuré ce jour-là, sur un conteneur
neuf : le premier appel télécharge le moteur de 16 Mo depuis GitHub (1,5 s),
les suivants coûtent 17 ms ; une retouche de `moteur/style.css` ou d'un
fichier JS n'ajoute rien au contexte, mais une retouche d'`index.html` y pousse
1 302 caractères qui demandent de trier un contraste « noir sur noir », sans
numéro de ligne : le détecteur, qui lit le fichier sans le rendre, ne résout
pas les couleurs, et `index.html` n'a aucun `#000`.

Le détecteur lancé sur `index.html`, `moteur/style.css` et `moteur/js` relève
23 constats : 8 polices « trop vues » (Instrument Serif), 7 filets latéraux,
déjà jugés voulus à l'action 28, les 2 faux contrastes, puis 5 points de
typographie (des capitales sur 34 caractères, signalées deux fois, un
interlignage de 1,25, un espacement de −0,11em sur « Entre deux
générations », la marge intérieure de `.encadre`), laissés au site. Le seul
audit consigné, celui de l'action 28, n'avait relevé « que ce qui est voulu ».
Ce qui compte se vérifie déjà mieux ailleurs : les contrastes par les tests,
dans les deux thèmes, l'écran par `test_ecrans.py`, les notes par
`scripts/notes_lighthouse.py`.

**Décision du propriétaire** : « Enlève les hooks ». Les deux entrées
(`PostToolUse` et `Stop`) quittent `.claude/settings.json` ; `impeccable
hooks off` pose `hook.enabled: false` dans `.impeccable/config.json`, pour
qu'une réparation par `/impeccable doctor` ne le rallume pas.
`test_le_detecteur_d_impeccable_ne_tourne_qu_a_la_demande`
(`tests/test_reglages_claude.py`) tient les deux. La compétence, ses agents et
ses exceptions restent, pour une critique ou une refonte demandée.
`scripts/setup_ui_tools.sh` signale désormais un hook revenu, au lieu d'un
hook absent ; `docs/outillage_interface.md` perd le plafond de 8 000
caractères, qui ne décrivait que le hook, et `test_prose.py` sa mesure.
