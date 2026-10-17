# Étape 3, le reste : la contribution employeur du FSPOEIE avant 2000, lue dans les décrets qui fixent son taux

**La demande.** La vague du 17 octobre 2026 : « Fais toutes les tâches qui
n'ont pas besoin de mes décisions ». Les étapes 3 à 9 étaient closes, et
aucune ne tenait plus de bloc « Reprise » ; il restait à la zone des données
une seule ligne, que la note de l'étape 3 léguait sans la ranger à une autre
étape, et que `contribution_employeur_public.csv` attribuait à l'étape 3 :
« le décret qui fixe 10,34 % en 1991 et 24 % en 1999, à lire dans la base
LEGI pour dater ces taux et les porter ». Le scénario 1 n'est pas touché.

## Ce que les textes disent

L'index DILA du dépôt (release `index-dila`, LEGI et JORF) suffit ; rien n'a
été retéléchargé.

- **Le décret n° 82-301 du 31 mars 1982**, que la base JORF résume : le taux de
  la contribution de l'État au régime des ouvriers est de « 9 % des
  rémunérations dues à compter du 01-04-1982 », au IV de l'article 28 du décret
  n° 65-836 du 24 septembre 1965.
- **L'article 28 du décret de 1965**, dans la base LEGI : six versions, la
  première ouverte le 2 avril 1982. Toutes portent « IV - Le taux de la
  contribution de l'Etat est fixé à 9 % des mêmes émoluments » jusqu'à celle
  du 1er janvier 2002, qui dit 24 %. Entre les deux, elles ne se coupent que
  sur la retenue du I : 6 %, 7 % le 30 décembre 1983, 7,7 % le 31 juillet
  1986, 7,9 % le 6 juillet 1988, 8,9 % le 31 décembre 1988.
- **Le décret n° 91-239 du 1er mars 1991**, article 3 : « Le taux de la
  contribution prévue au IV de l'article 28 du décret du 24 septembre 1965
  susvisé est fixé à 10,34 p. 100. Cette disposition est applicable aux
  rémunérations versées à compter du 1er février 1991. » Son article 1er
  porte la retenue à 7,85 % au même jour.
- **Le décret n° 98-1169 du 21 décembre 1998**, article 1er : le même taux
  « est fixé à 24 % », pour les rémunérations versées à compter du
  1er janvier 1999 ; son article 2 abroge à la même date l'article 3 du décret
  de 1991.

Les deux décrets fixent le taux à côté de l'article, sans le récrire : la
version de l'article ouverte le 31 décembre 1988 court donc jusqu'en 2002 sur
9 %, et sur une retenue de 8,9 % que le décret de 1991 avait déjà ramenée à
7,85 %. Ce n'est pas un décret perdu par la base — elle garde les deux —, mais
une consolidation en retard ; la lecture le signale, et c'est le décret qui
date le taux. Entre 1982 et 1999, la base JORF ne connaît aucun autre texte
qui touche au IV : ceux de 1983, 1986, 1987 et 1988 (deux) ne changent que la
retenue. Cette retenue est celle de la fiche `fspoeie` : 6 % jusqu'en 1983,
puis 7 %, 7,7 % au 1er août 1986, 7,9 % au 1er juillet 1987, 8,9 % au
1er janvier 1989 et 7,85 % au 1er février 1991. Et le texte du jaune — « fixé
en 1991 à 10,34 % », « porté à 24 % en 1999 » — date les mêmes taux, sans leur
jour ; son tableau 14 prend la suite à 24 % en 2000.

## Ce qui est porté

Sous la règle du 1er janvier : 9 % de 1983 à 1991 — 1991 le garde, le taux de
10,34 % ne prenant effet qu'au 1er février —, 10,34 % de 1992 à 1998, 24 % en
1999. Dix-sept années `certifiee` dans `contribution_employeur_public.csv`,
lues par `serie_fspoeie` (`scripts/fetch/dila_legi_contribution_employeur.py`),
qui date chaque taux par l'effet que son texte écrit, et certifiées par
`employeur_public_fspoeie_avant_2000` (`scripts/verifier_donnees.py`). La
série s'arrête en 1999, le jaune portant la suite : deux sources ne se
disputent pas une année. Avant 1983, rien : la base ne garde aucune version de
l'article d'avant le décret de 1982, et de 1930 à 1982 la part patronale reste
estimée par celle d'un salarié du privé.

Le test d'abord : la lecture, sur les textes cités (`test_verification.py`) ;
les repères et la couverture, 1983-2026 (`test_donnees.py`). Le README, la
méthodologie, les limites (`4-regimes-incomplets.md`) et l'en-tête du fichier
disent la nouvelle borne.

## Ce que cela déplace

Mesuré en refaisant le paquet et les témoins, que GitHub refera : aux
scénarios 4 et 6, dix-sept témoins sur 874, tous passés par le FSPOEIE,
baissent de 2,78 % en médiane, de 0,13 % (`limite_age_ouvrier_insalubre`) à
11,29 % (`statut_ouvrier_etat_1935`, actif ou non), 6,52 % pour
`statut_ouvrier_etat_1925` ; aucun ne monte. Les années lues pèsent donc moins
que la part patronale estimée qu'elles remplacent, seize sur dix-sept portant
9 ou 10,34 %. Rien ne bouge aux scénarios 1, 2, 3 et 5. La page Méthode compte
une série certifiée de plus.

## Ce qui reste

Rien pour la zone des données. Aucune étape de l'action ne tient de bloc
« Reprise » ; ce qui reste d'elles attend une décision du propriétaire — la
DREES refaite par le modèle (étape 8), l'indexation du stock du scénario 1
(étape 4), les cas types de l'étape 5 — ou une autre zone : L. 14, V, à lire
chez le service des retraites de l'État et la CNRACL (étape 9, le scénario 1),
les périodes d'AVPF quand la saisie les connaîtra (le site). L'action peut se
clore, comme le dit l'étape 8, une fois son premier point tranché.
