# La queue de `regenerer.py` et de `resumer_temoins.py`, par le hook de Bash

**Le 14 novembre 2026, la demande.** La session d'orchestration confie cette
étape, seconde vague du jour : joindre `regenerer.py` et `resumer_temoins.py`
à ce que le hook `.claude/hooks/bash.py` récrit. Il ne récrivait qu'un
`python -m pytest` lancé nu ; la consigne de `CLAUDE.md` nommait aussi ces
deux scripts, « à la main », et la note `2026-11-14-hook-de-bash.md` laissait
la question au propriétaire.

**Ce qui change.** Le motif `LONGUE` gagne une alternative :
`python (?:-m pytest|scripts/(?:regenerer|resumer_temoins)\.py)`. Un
`python scripts/regenerer.py` ou un `python scripts/resumer_temoins.py` lancé
nu, avec ou sans arguments, une affectation devant, devient
`set -o pipefail; <commande> 2>&1 | tail -n 30`. Le reste du motif est
inchangé : ni tube, ni redirection, ni commande composée, ni rien que le
shell étendrait. `.claude/settings.json` n'est pas touché : sa déclaration,
`if: "Bash(python *)"`, lançait déjà le script sur ces commandes. La puce
« Les sorties longues passent par `tail` ou `grep` » de `CLAUDE.md` dit
désormais que le hook s'en charge, sans une ligne de plus.

**La forme que le dépôt écrit**, relevée avant d'écrire le motif : partout
`python scripts/regenerer.py` (nu, `--verifier`, `--prose`, `--etapes`) et
`python scripts/resumer_temoins.py` (nu, `--depuis <révision>`,
`--extremes N`) — les en-têtes des deux scripts, les consignes de `src/`, de
`moteur/` et de `data/`, les agents de recherche. Le motif s'en tient à
cette forme. `python3 scripts/…`, `python ./scripts/…`, un autre script
passent tels quels.

**Ce que la queue garde de chacun.**

- *`resumer_temoins.py`* : rien ne lui est retiré. Son résumé tient en une
  ligne de tête, une par scénario et une pour les pages, huit lignes
  aujourd'hui, quels que soient ses arguments ; ses lignes sont longues, mais
  `tail` compte des lignes. Son aide en fait huit, son refus une. Un test le
  tient : si le résumé passait un jour trente lignes, il rougirait. Le gain
  est mince pour ce script : seule une trace d'erreur de plus de trente
  lignes y perd son début plutôt que sa fin.
- *`regenerer.py --verifier`* : une ligne par étape quand tout est à jour,
  douze en tout. Une étape périmée écrit tout son détail, et la dernière
  ligne nomme les étapes périmées : c'est elle que le plafond de 10 000
  caractères retirait à une vérification en échec.
- *`regenerer.py` nu, qui réussit* : onze étapes, chacune une ligne et les
  trois dernières de sa sortie, jusqu'à quarante-cinq lignes. La queue en
  retire donc le début, les premières étapes, et garde la fin, « tout est
  régénéré ». Qui veut les durées de toutes les étapes écrit son tube.
- *`--etapes` et l'aide* : cinq et douze lignes, entières.

**Le test d'abord.** Dans `tests/test_hook_bash.py`, huit commandes,
celles que le dépôt écrit, attendues récrites : vues rouges, le hook rendant
`None`, puis vertes une fois l'alternative écrite. Les deux lignes qui
disaient ces scripts laissés tels quels cèdent la place à ce que l'accord ne
couvre pas : un tube, une redirection, une commande composée, `python3`,
`python ./scripts/…`, un autre script. Le test du résumé qui tient dans la
queue était vert dès son écriture : il garde une propriété, il ne décrit pas
un comportement nouveau.

**Ce qui a agi en vrai, dans cette session**, le hook relu à chaque appel :
`python scripts/resumer_temoins.py`, nu puis avec `--depuis` et
`--extremes 3`, rendu entier avec la phrase du hook ; le même sur une
révision absente, « Exit code 1 » et son message ; `python
scripts/regenerer.py --verifier`, douze lignes, « tout est à jour (300 s) ».

**Ce qui n'est pas constaté** : un `regenerer.py` en échec de plus de 10 000
caractères, que rien ne mettait en échec ici ; une régénération complète en
écriture, non lancée. Ce que la note du hook laissait à constater le reste.

**L'accord pour la garde**, relu à sa source, dans la session d'orchestration
de la première vague. Elle écrit : « `regenerer.py` et `resumer_temoins.py`
ne sont pas récrits. […] Les joindre tient en une alternative du motif ; il
faudrait ton accord, puisque c'est une garde », et recommande « oui pour la
1 ». Le propriétaire, le 14 novembre 2026 à 19 h 12 UTC : « On utilise tes
recommandations ». L'accord ne couvre que ces deux scripts.

**Laissé de côté**, hors de l'accord : `python3`, `pytest` seul, un pytest ou
l'un de ces scripts dans une commande composée, `node --test`.
