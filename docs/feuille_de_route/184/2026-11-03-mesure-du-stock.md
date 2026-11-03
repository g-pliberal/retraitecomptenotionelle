# Le stock des rédactions sans statut final, mesuré par leur mot à mot

Mesuré le 3 novembre 2026, sur l'index LEGI du 2 novembre (`--recuperer`) et
la liste de contrôle du jour, pour répondre au propriétaire : « Les étapes 2
et 3 vont vraiment nous aider ? » Les étapes de l'action en sont sorties
revues (« Les étapes, revues le 3 novembre 2026 »).

**Comment la refaire.**

- *Le stock* : les rédactions de `data/reference/textes/redactions.csv` dont
  `retraite_notionnelle.noyau.textes.statuts()` rend `None`, « a_examiner »
  ou « a_rattacher » : 14 648, dont 14 645 dans l'index.
- *La précédente* d'une rédaction : dans l'index, la dernière version du même
  numéro (espaces et points ôtés) sous le même titre de texte, rangée par date
  de début puis par identifiant, qui a été en vigueur au moins un jour
  (`_a_vecu` de `scripts/fetch/dila_cherche.py`).
- *Identique* : `dila_cherche.difference(précédente, rédaction)` est vide ;
  *en succession* : la fin de la précédente est le début de la rédaction.
- *Ce qu'il faudrait lire* : la longueur des deux textes, NOTA comprise, contre
  celle du mot à mot.

**Ce qu'elle trouve.**

| Rédactions du stock | Nombre |
|---|---|
| sans précédente : des premières versions | 6 649 |
| identiques à la précédente, en succession | 984, dont 803 au code de la sécurité sociale |
| identiques, hors succession : doublons, trous | 20 |
| qui changent quelque chose | 6 992 |

Les 1 004 identiques se partagent en 907 sans statut, 86 « à examiner » et
11 « à rattacher » ; aucune n'a un texte vide. Pour les 6 992 autres, lire les
deux versions ferait 35,7 millions de caractères, le mot à mot 10,4 millions,
soit 29 % (25 % pour la rédaction médiane). Deux versions en vigueur au même
moment portent le même numéro dans le même texte pour 74 des 6 753 articles du
stock.

**Ce qu'elle ne dit pas.** Une rédaction qui change quelque chose peut rester
sans effet sur la fiche qui la cite : seul son mot à mot, lu, le dit. Les
6 649 premières versions se lisent en entier, quelle que soit l'étape.
