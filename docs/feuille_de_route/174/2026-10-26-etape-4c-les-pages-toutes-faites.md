# L'étape 4 (c) : les pages toutes faites

**Le 26 octobre 2026, la suite de « Vas-y, fait ça ici ».** Le routeur est sorti
d'`index.html` et chaque page a son dossier (`174/2026-10-26-etape-4b-les-pages-en-dossier.md`) ;
restait le pré-rendu. Chaque page est désormais écrite toute faite, et la
première chose qu'un navigateur reçoit est sa page, non une coquille vide qui
attend le moteur. Le détail de la décision est dans la note 0004
(`docs/decisions/0004-une-adresse-par-page.md`), l'état d'architecture dans
`docs/architecture/versions/2026-10-26-les-pages-toutes-faites.md`.

## Ce qui est fait

- **Neuf pages, fabriquées** : `scripts/construire_pages.py` met dans la coquille
  `moteur/page.html` le rendu de chaque page pour ses réglages par défaut — titre,
  description, adresse canonique, bandeau, corps, pied — et écrit l'accueil à la
  racine, les huit autres chacune dans son dossier, avec `sitemap.xml`.
  `regenerer.py` les refait (étape `pages`, après les témoins), `.gitattributes`
  les déclare fabriquées (`-merge`), `construire_pages.py --verifier` les dit
  périmées. `index.html` n'est plus la source des autres : on retouche la
  coquille, `pages.js` ou `gabarit.js`, jamais une page.
- **L'adresse canonique est celle de la copie du parti**
  (`https://partiliberalfrancais.fr/retraite/…`, décision 2 du propriétaire) ; le
  site sur GitHub Pages porte les mêmes fichiers et la même déclaration.
  `sitemap.xml` liste les neuf adresses.
- **La coquille ne demande que ce qu'il faut pour peindre** : la feuille de style,
  les deux polices (préchargées, sans quoi le chapeau perdait une ligne et tout
  le reste remontait) et `routeur.js`. Ni `modulepreload`, ni préchargement du
  paquet : chaque octet demandé avant la peinture la retarde.
- **Ce qui dépend de l'écran est écrit deux fois.** Les graphiques de Coût et de
  Droits non cotisés se dessinent à la largeur de la colonne, les deux schémas de
  Sankey d'une carte de Coût vont de front au large. Le générateur rend la page à
  une colonne de téléphone (360) et à une colonne de large (1040, schémas à 480),
  retrouve chaque tracé par un marqueur du gabarit (`marquerLesTraces`), et
  fusionne les deux rendus : `.variante-etroite` et `.variante-large` se
  partagent le tracé, la feuille de style en montre un seul, sous ou sur
  800 points d'écran. Un dessin convient à une colonne à 12 % près
  (`tracesConviennent`) : celui des schémas de front, 480, sert toutes les
  demi-colonnes de 432 à 532 points, de la tablette en largeur au bureau de
  1 440 ; au-delà de la tolérance, la fenêtre redessine la page par le moteur.
- **Le routeur anime sans recalculer** (`peutHydrater`, `hydrater`) : il replie
  les tableaux, branche le formulaire et les bascules, ouvre la section de
  l'adresse, mesure les légendes de ce qui se voit. Il n'attend ni le paquet de
  données ni le simulateur (`moteur()`, mémorisé) ; il les prépare pour ce que la
  page toute faite ne porte pas — des réglages ou une carrière derrière le `#`,
  une saisie retenue à reprendre, un tracé trop loin de la colonne —, et garde
  alors la hauteur de la page pendant le premier calcul. `body.dataset.pret`
  dit aux tests que la page est prête ; `main[data-prerendu]` dit que son
  contenu est celui du serveur, et part avec le premier redessin.
- **La suite suit** : `tests/test_pre_rendu.py` (les constantes, la tolérance, les
  marques de tracé, la feuille de style), `test_pages_en_dossier.py` (neuf pages
  à jour, leur corps égal à leur rendu, leurs deux dessins), le pilote des écrans
  (une fenêtre qu'on rétrécit : tolérée à 1 024 points, redessinée à 900) ;
  trois tests qui lisaient la coquille d'`index.html` lisent désormais les neuf
  pages (le pied hors de `<main>`, la description, aucun service extérieur dans
  aucune page) ; ceux qui gardaient les préchargements, et le style d'amorçage,
  qui n'existent plus, disparaissent.

## Les mesures, en local, le 26 octobre 2026

Lighthouse 13, l'arbre de travail servi d'ici (`python scripts/notes_lighthouse.py
--local`), avant (l'état publié à la fin de l'étape 4 (b)) et après, sur la même
machine. Accessibilité, Bonnes pratiques, SEO et Agentic sont à 100 partout, avant
comme après ; le CLS tombe à 0 partout.

| Page | Mobile avant | Mobile après (FCP, LCP, TBT) | Bureau avant | Bureau après |
|---|---|---|---|---|
| Programme | 57 | 97 (1,5 s, 1,8 s, 179 ms) | 80 | 99 |
| Simuler | 57 | 93 (1,6 s, 2,1 s, 273 ms) | 80 | 100 |
| Résultats | 57 | 67 (1,4 s, 1,7 s, 4 524 ms) | 79 | 71 |
| Coût | 57 | 92 (1,8 s, 2,1 s, 298 ms) | 80 | 100 |
| Pourquoi changer | 57 | 99 (1,5 s, 1,9 s, 9 ms) | 79 | 100 |
| Partager | 57 | 95 (1,8 s, 2,6 s, 0 ms) | 81 | 100 |
| Le saviez-vous ? | 57 | 99 (1,4 s, 1,9 s, 70 ms) | 80 | 100 |
| Carrières types | 57 | 97 (1,7 s, 2,3 s, 0 ms) | 79 | 100 |
| Droits non cotisés | 57 | 93 (1,8 s, 2,5 s, 196 ms) | 81 | 100 |
| Méthode et sources | 57 | 89 (1,6 s, 1,9 s, 402 ms) | 80 | 99 |

Avant, la page attendait le moteur pour peindre : 8 s au premier contenu en
mobile, 12,6 s au plus grand. Après, elle peint avec son HTML.

**En ligne**, le même jour, la suite verte et la copie déployée (GitHub Pages,
`python scripts/notes_lighthouse.py`) : Accessibilité, Bonnes pratiques, SEO et
Agentic à 100 sur les dix routes, CLS nul. Performance, avant l'étape 59 à 60 en
mobile et 87 à 90 au bureau :

| Page | Mobile | Bureau |
|---|---|---|
| Programme | 80 | 100 |
| Simuler | 86 | 99 |
| Résultats | 65 | 70 |
| Coût | 89 | 99 |
| Pourquoi changer | 83 | 100 |
| Partager | 97 | 100 |
| Le saviez-vous ? | 95 | 100 |
| Carrières types | 87 | 100 |
| Droits non cotisés | 85 | 100 |
| Méthode et sources | 83 | 99 |

En ligne, en mobile, le premier contenu et le plus grand sont plus longs et plus
dispersés qu'ici : de 1,2 à 2,7 s et de 1,5 à 3,9 s, sans que le poids de la page
l'explique (Coût, la plus lourde, est à 1,7 et 2,0 s). Une seule mesure par
page : à répéter avant d'en tirer quoi que ce soit.

## Ce que le chemin a appris

- **La colonne n'est pas celle qu'on croyait.** Le gabarit dessine à la largeur
  de la colonne, qui monte à 1 200 points d'écran avec des marges de `clamp()` :
  le seuil entre les deux dessins est à 800 points d'écran, non à 720, et le
  dessin large a été posé à 1 040 / 480 pour tolérer tout le large. Deux
  décalages en sont nés, que le pilote des écrans a vus avant Lighthouse : à
  1 440 points, le dessin de 420 était refusé, la page recalculée par le moteur,
  et le pied de page bougeait ; et sur les résultats, le formulaire tout fait
  (2 000 points de haut) cédait la place à l'écran d'attente le temps du premier
  calcul, et le pied revenait de 345 points (CLS de 0,244). La tolérance de 12 %
  et un verrou de hauteur pendant le premier calcul du moteur les ont supprimés.
- **La suite rapide ne voit pas les tests qui lisaient `index.html`** : quatre
  tests de `test_web*.py` n'ont rougi qu'à la lecture complète de ces fichiers.
  Pour un changement qui déplace ce qu'une page contient, les trois fichiers se
  jouent en entier avant l'envoi.
- **Local n'est pas en ligne.** L'état d'avant mesure 57 en mobile et 80 au
  bureau ici, 59 à 60 et 87 à 90 en ligne : le poste est plus lent que le réseau
  de l'hébergeur. Les comparaisons se font de local à local ; les chiffres en
  ligne se mesurent après le déploiement.
- **Le TBT qui reste tient aux tâches longues, non au volume des scripts.**
  Les audits de Lighthouse ne mettent que 96 à 134 ms au compte de
  l'évaluation des scripts de Méthode et du Programme en mobile ; le reste du fil
  principal est de la mise en page et de la peinture (300 à 640 ms de style et de
  mise en page sous un processeur ralenti quatre fois). Ce qui compte pour le
  TBT n'est pas le total mais la longueur de chaque tâche : voir plus bas.

## Le fil principal en mobile, mesuré après l'étape

Trois essais jetables, sur une copie de l'arbre (rien n'en est gardé), pour dire
où va le TBT de 180 à 400 ms des pages longues avant d'en promettre la baisse.

- **Le bruit est de l'ordre du résultat.** Trois mesures de la même page, le
  même arbre : TBT de 99 à 348 ms sur le Programme, de 208 à 398 ms sur Coût, de
  185 à 204 ms sur Méthode. Une comparaison à une mesure ne dit rien ; il en faut
  trois de chaque côté.
- **`content-visibility: auto` sur les sections hors écran** : la première
  mesure promettait une baisse nette (Méthode de 402 à 121 ms) ; trois mesures de
  chaque côté la ramènent au bruit, sauf peut-être sur le Programme. Non retenu.
- **Les gestes de l'animation, chacun dans sa tâche** (un `setTimeout` entre les
  sept appels de `hydrater`) : Méthode de 185-204 ms à 110-172 ms, le Programme
  de 99-348 à 35-143 ms, Coût sans changement.
- **Le routeur chargé seulement après l'événement `load`** (un script en ligne
  qui l'importe alors) : le premier contenu gagne de 0,2 à 0,8 s (de 1,2 à 1,3 s
  partout), mais le TBT passe de 30-340 ms à 450-760 ms, et la note de 92-99 à
  82-88 : le travail du routeur, qui se faisait avant le premier contenu et
  n'était pas compté, tombe dans la fenêtre du TBT. Charger plus tard ne vaut
  donc qu'une fois ce travail devenu léger.
- **Où va le temps** (trace Chrome, Méthode, processeur ralenti quatre fois) :
  l'évaluation du graphe de modules est UNE tâche de 201 ms (`v8.evaluateModule`),
  qui contient le démarrage du routeur donc l'animation de la page ; la mise en
  page en pèse 154 en quatre passes, dont des passes forcées par la mesure des
  tableaux (`plierLesTableaux`, `texteMontre`). Le profil du JavaScript propre
  est petit, une centaine de millisecondes en tout. Lighthouse simule le
  ralentissement en multipliant par quatre les tâches qu'il observe : toute
  tâche de plus de 12,5 ms sans ralentissement compte, au-delà de 50 ms simulées.
  Pour passer à zéro, il faut donc un graphe de modules qui s'évalue en tâches
  courtes — l'étape 5, qui sort du démarrage le code que seules les simulations
  utilisent — et une animation découpée, avec des mesures groupées (lire toutes,
  puis écrire toutes).

## Ce qui reste

- **Le TBT et le premier contenu en mobile** : de 80 à 97 en ligne pour les neuf
  pages hors résultats. C'est l'étape 5, le moteur à la demande : le démarrage
  du routeur ne doit plus évaluer que de quoi animer la page, le reste
  (`pages.js`, la saisie, le contexte, les étapes du droit : un graphe d'1 Mo
  compressés, dont `pages.js` 270 Ko) se chargeant au premier calcul ; et
  l'animation se découpe en tâches courtes, ses mesures groupées. Une fois le
  démarrage léger, charger le routeur après le premier contenu devient un gain.
  Les mesures sont bruitées : trois de chaque côté, avant de conclure.
- **Le sort des résultats d'une simulation** (décision 3, au propriétaire) :
  67 en mobile, 71 au bureau tant que le moteur calcule avant d'afficher.
- **L'hôte à sa prochaine copie** : la copie doit emporter les neuf pages et
  `sitemap.xml`. Tant qu'elle ne l'a pas fait, l'adresse canonique que chaque
  page déclare (`partiliberalfrancais.fr/retraite/cout/`…) répond 404 chez lui :
  les moteurs de recherche retiennent une adresse qui n'existe pas encore.
  Ses deux retouches d'`index.html` (`plf-theme.css`, le bandeau
  `plf-back-link`) ne couvrent plus que l'accueil ; la classe `plf-embedded` de
  son cadre se pose à chaque chargement. Il peut aussi déclarer le plan du site
  dans son `robots.txt` (`docs/integration-partiliberalfrancais.md`).
