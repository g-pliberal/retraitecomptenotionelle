# Les skills du compte masqués pour ce dépôt

**Le 12 novembre 2026, la demande.** Le propriétaire, la liste de la note
« Le contexte de départ, constaté » lue : « On déconnecte les skills et
connecteurs inutiles sur ce projet », « On raccourci la course », et, sur
Sonnet : « J'ai pas suivi ». Cette note fait le premier point ; le deuxième
attend une session neuve.

**Ce que le dépôt peut, contre ce que les notes disaient.** La note du
11 novembre, puis celle du matin, renvoyaient les quatorze skills du compte
claude.ai (`anthropic-skills:…`) au propriétaire, sur claude.ai, où le
réglage vaut pour tous ses projets : `skills.md` dit « turn the skill off
for your claude.ai account ». L'essai dit autre chose. Un réglage local, non
commité, `skillOverrides` à `off` pour `anthropic-skills:morning` et pour
`import-memory`, sous son nom court : le sous-agent témoin lancé ensuite
n'annonce plus que douze skills du compte, et les quatorze reviennent une
fois le réglage ôté. `skillOverrides` masque donc un skill du compte, pour
ce dépôt seulement.

**Ce qui est fait**, dans `.claude/settings.json`, une garde, à la demande
du propriétaire.

- *Huit skills éteints* (`off`), sans objet ici : `artifact-emulator`,
  l'artifact étant coupé ; `built-in-browser`, `chrome-browser` et
  `computer-use`, qui pilotent le poste ; `docs` et `google-workspace`, dont
  les connecteurs sont refusés ; `import-memory` et `morning`.
- *Cinq à la demande* (`user-invocable-only`) : `deep-research`, `docx`,
  `pdf`, `skill-creator` et `xlsx`. Leur description n'entre plus dans chaque
  requête, et le propriétaire les appelle encore par leur nom, `/pdf`
  (`skills.md`, « Override skill visibility from settings » : « Hidden » pour
  Claude, « Yes » au menu). Ce second point n'est pas constaté : seul le
  propriétaire tape une commande.
- *Un gardé* : `pptx`, d'où sortent les deux présentations aux adhérents de
  `docs/`.
- `tests/test_reglages_claude.py` tient les trois listes.

**Constaté** sur un sous-agent témoin d'un seul appel, sur Haiku, à la même
question avant et après : `anthropic-skills:pptx` seul reste annoncé ; la
liste des skills passe de 16 302 à 6 369 caractères, et le premier appel de
29 278 à 26 176 jetons, 3 100 de moins. Une session neuve doit en perdre
autant sur ses 43 500.

**Les connecteurs : essayé, sans effet.** `managed-mcp.md` donne
`deniedMcpServers` pour « Any settings scope », et `mcp.md` dit qu'il filtre,
dans une session du cloud, les connecteurs que la plateforme livre. Essayé
au réglage local, par `serverName`, sur `Claude_Docs` et les quatre
connecteurs Google, sous le nom que la session leur donne : un témoin lancé
ensuite reçoit toujours les consignes des six serveurs. Elles ne partent
donc pas depuis le dépôt, du moins en cours de session ; rien n'est commité.
Restent 600 jetons, que le propriétaire n'ôterait qu'en déconnectant ces
connecteurs sur claude.ai, pour tous ses projets. Appris au passage : un
sous-agent ne reçoit les consignes des serveurs qu'après son premier appel
d'outil.

**Sonnet, redit au propriétaire.** La note du 3 novembre proposait d'ouvrir
sur Sonnet 5.5, au quart du tarif de Fable 5.2, les sessions que les tests
tiennent serré, et de comparer leur coût. C'est la question du modèle, à un
cran de plus : le propriétaire gardant Fable 5.2 pour l'instant, elle est
sans objet tant que ce choix tient.

**Ce qui reste.** La course de GitHub, que le propriétaire a décidé de
raccourcir : une session neuve, qui mesure d'abord ce que la mémoire des
calculs rendrait sur les 18 minutes de la suite et les 5 de la fabrication.
