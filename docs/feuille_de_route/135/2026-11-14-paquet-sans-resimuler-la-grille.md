# Le paquet refait sans resimuler la grille du coût

**Le 14 novembre 2026, la demande.** Le propriétaire : « fait les trois » ; le
troisième point de la note du même jour
(`2026-11-14-correction-sans-attendre-le-verdict.md`) : rendre
`python scripts/construire_donnees.py` plus rapide après un changement du
modèle ou des données d'un régime. Chaque correction de l'action 130 le lance
avant ses tests, la mémoire des calculs vidée par sa propre retouche.

**La mesure, avant de toucher au code.** Des chronomètres posés autour des
grandes étapes du script et de `memoire.memoriser`, la mémoire des calculs
vide, dans un conteneur de session à quatre cœurs : 238,2 s ce jour-là
(151,7 s relevés le matin dans un autre conteneur ; les deux machines ne se
comparent pas, seuls l'avant et l'après d'une même machine se comparent).

| ce que le script fait, dans l'ordre | durée |
|---|---|
| le paquet sans ses tables, écrit deux fois | 4,2 s |
| le coût de référence : sa grille simulée, 23,5 s, puis ses masses, 8,1 s | 31,9 s |
| l'engagement acquis du bilan, dont la même grille resimulée, 21,3 s | 24,0 s |
| les carrières types et les exemples, par le portage | 6,4 s |
| le coût des avantages | 11,9 s |
| le coût sous l'espérance de vie basse, puis haute : une grille et des masses chacun | 64,0 s |
| le coût sous quatre variantes de fécondité et de migrations, sur la grille gardée | 47,1 s |
| le bilan du compte, dont la même grille resimulée deux fois, 43,8 s | 47,6 s |

Deux constats. La grille du coût (`cout._pensionnes`), sous les réglages de
référence, se simulait quatre fois, vingt secondes chacune : une fois pour le
coût, que la mémoire garde, puis une fois pour l'engagement acquis du bilan
et deux fois pour le bilan du compte, qui ne la demandaient pas à la mémoire.
Et tout se calcule en série : 287 s de processeur pour 238 s d'horloge, sur
quatre cœurs.

**Ce qui est fait.** La grille simulée se garde sous une seule clé, celle que
`memoire.cout` lui donnait déjà, et se demande par `memoire.grille_du_cout`.
`calculer_engagements` reçoit une grille déjà simulée (`grille_simulee`,
comme `calculer_cout`) ; le bilan du paquet (`_bilan`) et le bilan du compte
(`calculer_bilans`) la lui passent, et ce dernier s'en sert aussi pour ses
profils. Aucune règle ni aucune donnée ne change : ce sont les mêmes calculs,
faits une fois.

- *Les tests, vus rouges d'abord* : l'engagement ne resimule pas la grille
  reçue et rend le même résultat (`tests/test_cout.py`) ; le bilan du compte
  ne la simule qu'une fois (`tests/test_bilan_compte.py`) ; la grille demandée
  seule et celle du coût partagent leur clé (`tests/test_outillage.py`) ; le
  bilan du paquet passe à l'engagement la grille gardée (`tests/test_web.py`).
- *Vérifié* : les quatre fichiers que le script écrit ont la même empreinte
  avant et après, sur le même arbre ; 238,2 s puis 167,5 s, mémoire vide,
  soit 71 s de moins ; la suite rapide et les tests de la zone verts.
- *Le paquet du dépôt différait déjà de celui que le script rend*, avant
  comme après : une correction de l'action 130 que GitHub n'avait pas encore
  refabriquée. Il n'est pas commité ici.

**Ce qui reste à prendre**, sur les 168 s : trois grilles, 65 s (référence,
espérance de vie basse et haute) ; sept fois les masses du coût, 70 s ; les
avantages, 12 s ; le reste, 20 s.

- *Répartir sur les cœurs* les calculs qui ne dépendent pas l'un de l'autre :
  les trois grilles et les avantages d'abord, les masses des sept coûts
  ensuite. Attendu, non mesuré : de 60 à 80 s sur quatre cœurs. À écrire avec
  la mémoire des calculs, qui sait déjà faire attendre un processus sur le
  calcul d'un autre, et à vérifier quand elle est coupée
  (`CALCULS_SANS_MEMOIRE=1`).
- *Les grilles sous l'espérance de vie basse et haute* : non regardé, si
  elles diffèrent de celle de référence par autre chose que leurs survies.
- *Les masses du coût, de 8 à 12 s, sept fois* : non profilées.
- *Une mémoire indexée plus finement que le modèle entier* : écartée sans
  essai. Toute donnée d'un régime peut déplacer la grille, et rien ne dit
  aujourd'hui ce qu'un calcul a lu.
