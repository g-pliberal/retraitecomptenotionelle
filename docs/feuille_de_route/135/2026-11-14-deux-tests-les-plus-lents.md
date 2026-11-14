# Les deux cas les plus longs de la suite, raccourcis sans rien céder

**Le 14 novembre 2026, la demande.** La note
`2026-11-14-course-en-travaux-paralleles.md` laissait ouvert : « la tranche
la plus longue tient à son test le plus long, non au nombre de machines :
raccourcir les deux tests de huit et neuf minutes, ou les découper, avant
d'ajouter des tranches ».

**Les deux cas, relevés aux journaux de GitHub** (`--durations=25` de chaque
tranche) :

- *la préparation de l'étude de l'indexation du scénario 6*
  (`tests/test_indexation_scenario_6.py`, la fixture `etude`) : 596 à 618 s
  au second essai sans mémoire, la tranche 1 bloquée dix minutes sur elle.
  Avec la mémoire des calculs, elle ne coûte presque rien.
- *la confrontation de la façade au jumeau Python sur tous les témoins*
  (`tests/test_facade_jumeau.py`) : 262 s sans mémoire, 358 s à la première
  course de `main` avec mémoire, où elle fermait seule la tranche 4 ; et le
  même pour le scénario 1, 120 à 181 s. La mémoire n'y peut rien : rien ne
  s'y garde. Le temps est au moteur Python (mesuré sur un témoin sur
  quarante : 6,7 s de jumeau, 1,4 s de façade, 0,6 s de comparaison).

**L'étude ne chiffre que ce que ses tests lisent.** Elle chiffrait chacune
des dix-huit voies sous chacune des trois trajectoires, une soixantaine de
calculs du coût ; ses tests en lisent onze. `etudier(seulement=…)` ne
chiffre que les couples nommés ; la baisse de la voie 2 et les primes de la
voie 1, dont chaque résultat dépend, se calculent toujours, et rien d'autre
ne change dans la boucle : chaque résultat lu est celui de l'étude entière.
Le script, lancé à la main, chiffre toujours tout. Un test dit que l'étude ne
rend que ce qu'on lui demande, vu rouge d'abord. Mesuré ici, en série, la
mémoire vide : la préparation passe de 490 s à 115 s, le fichier de 586 s à
217 s.

**La confrontation en huit parts.** Les deux confrontations de tous les
témoins se découpent en huit cas paramétrés (`PARTS`), un témoin sur huit
chacun, que le vol de tâches répartit entre les processus. Ce que chaque cas
tenait d'un tenant passe ailleurs, sans rien perdre :

- *chaque témoin confronté une fois* : un test dit que les parts réunies sont
  tous les témoins, plus de neuf cents, chacun une fois ;
- *chaque type relu* : un test sert tous les témoins par la façade seule, une
  minute de node, et y trouve chaque type rare du scénario 1 et de la
  comparaison ; chaque part confrontant champ par champ tout ce que la façade
  sert, chacun y est confronté au jumeau ;
- *les quatre fiches de paie que le jumeau ne refait pas* : chacune doit
  encore s'écarter, dans la part qui la porte.

Mesuré ici, sur trois processus : le fichier entier en 3 min 30, son plus
long cas en 52 s (les types), une part de la comparaison en 41 à 45 s.

**Ce qui reste.** Relever, sur la première course de `main` sans mémoire, la
tranche la plus longue : elle devrait tenir à la somme de ses fichiers, et
non plus à un cas. La préparation de l'étude, à deux minutes, reste le plus
long cas qui ne se découpe pas.
