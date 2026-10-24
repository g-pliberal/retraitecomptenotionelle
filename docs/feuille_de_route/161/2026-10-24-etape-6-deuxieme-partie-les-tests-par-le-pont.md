# Étape 6, deuxième partie : les tests qui lisaient la saisie Python passent par le pont

**La demande.** La vague du 24 octobre 2026 : onze sessions, une tâche
chacune, que le propriétaire ne suit pas pas à pas. Celle-ci tient le premier
des trois lots restants de l'étape 6 : la trentaine de fichiers de tests qui
lisent la saisie Python, portés sur le pont (`pont.carrieres_des_saisies`),
les témoins identiques à l'octet.

**Le pont reste ouvert** (e4de3b4). Un test demande une carrière à la fois :
le pont lancé pour une seule demande coûtait trois dixièmes de seconde — node,
ses modules, le paquet de 5,8 Mo —, la saisie Python cinq millièmes. Sans
paquet, `pont.py` garde `pont.mjs --servir` ouvert sur `moteur/donnees.json`,
et le relance quand la fabrique le récrit (sa date, sa taille) : une demande
coûte quelques millièmes. `construire_temoins.py --verifier` trouve les
témoins à jour, octet pour octet. La suite rapide, mesurée sur ce conteneur à
quatre cœurs, a passé de 92 s avant le portage à 84 s après lui (2 974 tests).

**La saisie par la pension** (28d96ed). Le pont rendait d'une saisie par la
pension une carrière au revenu de la saisie, sans rien dire. Il rend celle
que le contexte du portage trouve en inversant la pension, celle que le site
simule, sans le niveau trouvé (`niveau_inverse`), que le portage seul garde.

**L'aide des tests** (`tests/outils_pont.py`). `Saisies` fait d'une requête
ce que le contexte Python en faisait : la carrière et les paramètres que le
pont rend, un simulateur Python par jeu de paramètres, la simulation, et
`RefusDuPortage` pour un refus. `saisie_du_portage` lit la requête dans la
saisie du portage, par `site()`, sur les présomptions du paquet, lues une fois
par processus : le paquet entier passait le fil à chaque lecture, un quart de
seconde. `refus_de_la_saisie` cherche le motif d'un refus dans sa ligne, et
non dans la pile qui la suit.

**Les règles du portage**, que la première partie prévoyait :

- qui éprouve une règle du moteur par une saisie simule au moteur Python la
  carrière que le pont bâtit, ses assertions inchangées : les majorations
  pour conjoint et pour enfants, le minimum de la SNCF, les PCV, les
  versements uniques, le RAFP, les indépendants, le décompte des services,
  les droits contrefactuels, la réversion, l'invalidité, l'étranger, les
  départs, le cumul, le relevé prolongé, et les moitiés Python de la
  liquidation et des étapes du droit, de Destinie et de TRAJECTOiRE ;
- qui éprouve la saisie elle-même — un refus, ce qu'elle lit, l'adresse
  qu'elle réécrit, le relevé que le contexte prolonge, l'inversion d'une
  pension — la lit dans le portage, par `site()` ; une date de la saisie s'y
  compare en année et mois, `DateMois` étant un objet du portage ;
- une confrontation des deux saisies ne garde que ce que le portage lit, et
  ses assertions écrites à la main : les dispenses, le temps partiel, le
  conjoint collaborateur. La Lodeom et la réversion agricole gardent celle
  des deux moteurs sur la fiche de paie et la PMR, l'étranger et
  l'invalidité sur les vues de la carrière, que chaque moteur tire de sa
  chronologie. La saisie Python ne se confronte plus au portage que par les
  témoins (`test_pont.py`), jusqu'à son retrait ;
- `Montants` est la saisie : ses tests lisent les montants du portage, aux
  valeurs posées à la main ; la cotisation des régimes spéciaux, du barème
  (`remuneration.py`), garde ses deux moteurs. Le cas de moins de quinze ans
  d'assurance française, qu'un objet factice faisait, est une carrière :
  trente-quatre ans au Maroc, neuf ans et demi en France ;
- sans saisie : l'oracle lit le temps partiel de ses exemples, le
  micro-social ses abattements dans la table, que la saisie du portage
  applique ; l'âge maximal de la saisie se déduit de l'âge terminal des
  tables ; le simulateur des réglages de référence se prend sans contexte.

Trente-neuf fichiers de tests ne lisent plus ni la saisie ni le contexte
Python. La garde des présomptions (`PRESOMPTIONS_DECALEES=1`) passe sur
chacun ; elle n'y mesure plus ce que la saisie présume, que le portage lit
dans le paquet, que la mesure ne décale pas.

**Tests.** 2 974 rapides ; chaque fichier porté, en entier ; le pont.

**Ce qui reste du premier lot**, quinze fichiers.
1. Le site : `outils_web.py`, `test_web.py`, `test_web_saisie.py`,
`test_web_revues.py`, `test_formulaire.py`, `test_estimation_du_site.py` —
l'échelle, les départs de l'estimation, et les confrontations des deux
saisies du formulaire. La session du site (action 173) touche les mêmes
fichiers : à mener avec elle, ou après elle.
2. Le centre du coût, deuxième lot : `test_agregats.py`,
`test_bilan_compte.py`, `test_cout.py`, `test_affirmations.py`,
`test_outillage.py` (le coût du contexte). Les exemples figés de
`test_cout.py` gardent leur saisie en champs, que `carrieres_des_saisies` ne
lit pas : `pont.saisies` les lit, il les simule au portage.
3. Le retrait, troisième lot : la référence de `test_pont.py`, et les gardes
qui interdisent la saisie Python (`test_estimation_officielle.py`, le budget
de `test_outillage.py`), qui tombent avec elle.
