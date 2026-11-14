# Deux blocs « Reprise » d'étape ôtés des notes de l'action 186

*Le 14 novembre 2026, action 135, troisième vague de petites corrections,
lancée par la session d'orchestration. La session qui a mis
`python scripts/reprise.py 186` sous le plafond de Bash
(`2026-11-14-reprise-sous-le-plafond.md`) a relevé trois notes de
l'action 186 dont le bloc « Reprise » d'étape semblait n'attendre plus rien.
La règle (`.claude/rules/documentation.md`) : chaque étape inachevée tient le
sien, sous le titre de sa note, et l'ôte en finissant ; elle ne demande pas de
ligne de clôture à sa place.*

- **`186/2026-11-07-planchers-etude.md`** : bloc ôté. Il disait « Cette note
  n'a plus rien à faire » ; la suite est à deux autres notes
  (`…-invalidite-caisses.md`, `…-invalidite-questions.md`), puis au modèle.
- **`186/2026-11-09-rendement-net.md`** : bloc ôté. Il disait de même ; la
  seule chose en attente, faire confirmer au propriétaire que l'argument
  « net du déficit, la proposition rend plus » tombe avec le rendement retiré
  du site (décision 127), est déjà inscrite dans « Ce qui reste ouvert » de
  `186/2026-11-13-questions-au-proprietaire.md`. Rien ne se perd.
- **`186/2026-11-09-protocole-test.md`** : bloc gardé. Le protocole est
  écrit, mais le test lui-même attend la refonte du site (décision 137), et
  ses réglages — quotas, qui mène, données — n'ont pas reçu de réponse un à
  un : les pistes de la note en tiennent lieu. L'étape attend donc encore
  quelque chose, et c'est ce bloc qui le dit à la session qui mènera le test.

Le bloc de l'action 186 dans `docs/feuille_de_route.md` ne nomme aucune de ces
étapes : il n'est pas touché.

La règle et le contrôle se contredisent : la règle veut que l'étape ôte son
bloc en finissant, mais `scripts/conservation.py` compte le bloc ôté comme une
perte ; les deux blocs sont donc recopiés ci-dessous, mot pour mot, chaque ligne
décalée d'une espace pour que `reprise.py` ne les prenne pas pour des blocs
en cours.

## Les blocs ôtés, tels qu'ils étaient

De `186/2026-11-07-planchers-etude.md` :

 **Reprise, au 7 novembre 2026.** Le propriétaire a tranché (décisions 62 à
 66, 69 et 78) : planchers gardés tant que leur caisse a des réserves, la
 garantie ensuite, dès la bascule pour la CNRACL, l'État, la SNCF et la
 complémentaire agricole ; la garantie ouverte dès l'invalidité, pour tous les
 invalides. Deux sessions neuves, ouvertes le même jour, mènent la suite :
 la vérification caisse par caisse (note `…-invalidite-caisses.md`) et les
 cinq questions (note `…-invalidite-questions.md`), que le propriétaire
 garde ouvertes pour y réfléchir. Cette note n'a plus rien à faire. Le modèle
 n'est touché qu'après, par une session du modèle, au seul scénario 6.

De `186/2026-11-09-rendement-net.md` :

 **Reprise, au 13 novembre 2026.** Le rendement net est chiffré. Le
 propriétaire a tranché le 13 novembre : le rendement ne se montre plus sur le
 site (décision 127). L'argument « net du déficit, la proposition rend plus »,
 faux au modèle, n'a donc plus de place ; c'est la lecture de la session, à lui
 confirmer. Cette note n'a plus rien à faire.
