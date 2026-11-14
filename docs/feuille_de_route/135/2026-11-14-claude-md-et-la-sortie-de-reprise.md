# `CLAUDE.md` décrit la sortie de `reprise.py` d'après `9d01388`

**Le 14 novembre 2026**, à la demande de la session d'orchestration
(troisième vague, correction C1). Depuis `9d01388`
(`2026-11-14-reprise-sous-le-plafond.md`), `reprise.py <numéro>` réduit
chaque étape inachevée à une ligne quand la sortie dépasse le plafond de
Bash, et le bloc d'une étape se lit par un mot du nom de sa note. `CLAUDE.md`
disait encore « les blocs d'une action et ses trente dernières notes », et
renvoyait, pour le bloc d'une étape, à `reprise.py <action>`.

**La sortie, vue avant d'écrire.** `reprise.py 138` (7 282 caractères) :
le bloc, les trente dernières notes de 272, puis « Étapes en cours : 16, une
ligne chacune ». `reprise.py 138 etape-14` : le bloc et les notes dont le nom
porte « etape-14 ». `reprise.py 47` : bloc et notes, sans étape.

**Ce qui change**, à longueur égale (198 lignes) : la règle « Au démarrage »
dit les deux formes de la commande et la ligne par étape ; la liste « Au
début d'une étape » renvoie à `reprise.py <action> <mot de sa note>`. La
phrase de l'introduction (« `reprise.py 138` imprime celui d'une action »)
reste vraie. Aucun test ne tient ces phrases ; `test_consignes.py`, qui lit
`CLAUDE.md`, reste vert.

**Publié par l'orchestration.** La session de C1 n'avait pas le dépôt dans
ses sources, et n'a pu pousser (403 du proxy git) : la session
d'orchestration a appliqué son changement, vérifié la sortie de
`reprise.py 138` et de `reprise.py 138 etape-14`, puis publié.

**Reste** : `.claude/agents/eclaireur.md` et `Explore.md` disent encore
`reprise.py <action>` pour les blocs ; vrai pour l'action, incomplet pour
l'étape. Hors de cette correction.
