# La proposition des adresses : une adresse par page

**Le 26 octobre 2026, la demande.** Le propriétaire : « Fait moi la
proposition pour 1. Je veux être sûr avant de faire un changement. » La
décision 1 de l'action 174 : donner à chaque page du site sa propre adresse,
condition du pré-rendu. Cette note ne change rien au site ; elle dit ce que la
décision engage, et comment on la mènerait sans rien casser.

**Pourquoi une adresse par page.** Le serveur ne reçoit jamais ce qui suit `#`
dans une adresse : pour lui, les neuf pages n'en font qu'une, `index.html`, qui
choisit la sienne une fois ses scripts chargés et le moteur prêt. Il ne peut
donc envoyer à chacune son contenu tout fait. Or c'est ce contenu tout fait,
affiché sans attendre le moteur, qui porte la Performance à 100 : 98 à 100 en
mobile sur des pages figées (note du diagnostic), contre 59 à 60 en ligne
aujourd'hui.

## Les adresses proposées

| Page | Aujourd'hui | Proposé |
|---|---|---|
| Programme | `…/` | `…/`, inchangée |
| Simuler | `…/#/simuler` | `…/simuler/` |
| Une simulation | `…/#/simuler?naissance=…` | `…/simuler/#naissance=…` |
| Coût | `…/#/cout` | `…/cout/` |
| Pourquoi changer | `…/#/risque` | `…/risque/` |
| Partager | `…/#/partager` | `…/partager/` |
| Le saviez-vous ? | `…/#/saviez-vous` | `…/saviez-vous/` |
| Carrières types | `…/#/cas-types` | `…/cas-types/` |
| Droits non cotisés | `…/#/avantages` | `…/avantages/` |
| Méthode et sources | `…/#/methode` | `…/methode/` |
| Une page sous d'autres réglages | `…/#/cout?indexation=prix` | `…/cout/#indexation=prix` |

`…` vaut `g-pliberal.github.io/retraitecomptenotionelle` ou
`partiliberalfrancais.fr/retraite`. Les noms restent ceux d'aujourd'hui : chaque
ancienne adresse a sa nouvelle, une pour une.

**La règle : la page avant le `#`, le lecteur après.** Ce qui désigne la page
passe dans le chemin, que le serveur lit, pour qu'il la serve toute faite. Ce
qui appartient au lecteur — sa carrière, ses réglages — reste derrière le `#`,
que le navigateur ne transmet à aucun serveur : la promesse « rien n'est envoyé
à un serveur » tient comme aujourd'hui. Écrire la carrière en paramètres
(`simuler/?naissance=…`) l'aurait inscrite dans les journaux de GitHub et de
l'hébergeur du parti ; c'est la raison de garder le `#` pour elle.

## Les anciennes adresses restent valides, toutes

Une ancienne adresse a toujours la forme `…/#/…`, et le serveur y sert la page
d'accueil, quoi que porte la suite. Un court script, le premier de l'en-tête de
l'accueil, lit cette suite et remplace l'adresse par la nouvelle :
`#/cout?indexation=prix` devient `cout/#indexation=prix`, `#/simuler?…` devient
`simuler/#…`, l'ancienne simulation sur `#/?…` mène au simulateur, `#/trajectoire`
et `#/donnees` à la page qui les remplace, section ouverte, comme aujourd'hui.
Il remplace l'adresse sans l'empiler : « précédent » ne ramène pas à
l'ancienne. Une ancienne adresse coûte un chargement de plus, une fois, avant
que le moteur ne parte. Les partages déjà publiés, les marque-pages, les liens
du site du parti — dont le lien recommandé `/retraite/#/simuler` — mènent où ils
menaient, sur GitHub Pages comme sur la copie, puisque tout se passe dans le
navigateur.

## Ce qui change pour le lecteur

- *L'affichage.* Une fois le pré-rendu fait (étape 4), chaque page s'affiche
  sans attendre le moteur. Avant lui, la vitesse ne change pas : c'est le
  pré-rendu qui la donne, et l'adresse qui le permet.
- *Le titre.* Chaque page a le sien dans l'onglet, dans les favoris et dans les
  moteurs de recherche, qui ne voient aujourd'hui qu'une page.
- *Le passage d'une page à l'autre recharge une page.* Mesuré le 26 octobre
  2026 sur le site en ligne, poste de bureau sans bridage : aller aujourd'hui de
  page en page par l'ancre, moteur gardé, prend 0,37 s jusqu'au Coût rendu ;
  recharger une page, cache du navigateur plein, 0,7 à 1,0 s pour une page de
  contenu et 2,4 s pour des résultats, le temps que le moteur se réinitialise ;
  ouvrir les résultats à froid, 6,4 s. Pré-rendues, les pages de contenu
  n'attendent plus le moteur ; les résultats, et une page vue sous d'autres
  réglages, l'attendent encore. Sur un téléphone, ces temps se multiplient.
  Simuler, lire le Coût, revenir aux résultats paiera deux fois
  l'initialisation du moteur, quand on la paie une fois aujourd'hui. Si cela
  gêne, la navigation pourra plus tard se faire sur place, la page suivante
  chargée sans quitter la première ; rien n'y oblige pour commencer.
- *Les réglages.* Un lecteur qui en a changé un voit d'abord la page sous les
  réglages par défaut, seuls que connaisse la page toute faite, puis sous les
  siens. Pour qu'il ne lise pas un chiffre qui n'est pas le sien, elle
  s'estompe le temps du calcul, comme aujourd'hui sur place, jusqu'à ce que la
  sienne la remplace.
- *Le sommaire d'une page.* Ses liens deviennent de vraies ancres
  (`#cout-depenses`), qui marchent même avant les scripts ; le script continue
  d'ouvrir la section repliée qu'ils visent.
- *Inchangés* : le bouton « précédent », les marque-pages, le partage d'un
  graphique, qui reprend l'adresse de la page ; le brouillon du formulaire,
  gardé dans le navigateur, que toutes les pages lisent puisqu'elles ont la
  même origine ; la signature des images partagées
  (`partiliberalfrancais.fr/#simulateur`) ; le contenu des pages.

## La copie de partiliberalfrancais.fr

Elle se fait en recopiant le dépôt tel quel (`docs/integration-partiliberalfrancais.md`),
sans règle de réécriture côté serveur, et ce document lui promet des adresses
qui « ne changeront pas sans que ce fichier le dise ». La proposition tient les
trois engagements.

- *Sans réécriture.* Une page est un dossier qui porte son `index.html` : tout
  serveur statique sert `…/cout/`, et redirige `…/cout` vers `…/cout/`, comme
  il redirige déjà `/retraite` vers `/retraite/`. GitHub Pages le fait (vérifié
  le 26 octobre 2026 sur `…/moteur`).
- *Les anciennes adresses*, par la redirection, faite dans le navigateur.
- *Le document d'intégration* dit le changement le jour où il part : la
  nouvelle table des adresses, le lien recommandé `/retraite/simuler/`, la
  liste de vérification après une mise à jour de la copie.

Deux points à dire à l'hôte, qui ne bloquent pas :

- *Ses deux retouches* (`plf-theme.css`, le bandeau `plf-back-link`) sont faites
  dans `index.html`. Avec une page par dossier, il faudrait les refaire dans
  chacune. Le document lui recommande déjà de les abandonner, depuis le
  17 septembre ; ce sera le moment.
- *Le cadre de `/#simulateur`.* Changer de page y chargera une nouvelle page
  dans le cadre. Le simulateur règle lui-même la hauteur du cadre à chaque
  rendu, et le fera à chaque chargement. La classe `plf-embedded`, que pose le
  script de l'hôte, doit l'être à chaque chargement du cadre et non une seule
  fois : à vérifier avec lui. Sinon, seule la ligne « Un outil du Parti libéral
  français » réapparaît en pied de page, ce qui ne casse rien.

## Deux formes possibles, une recommandée

- *Des dossiers*, `…/cout/` : chaque page est `cout/index.html`. Tout serveur
  statique les sert sans réglage. Les chemins de la page changent d'un niveau
  (`../moteur/style.css`), et le pré-rendu les écrit pour chacune.
- *Des fichiers*, `…/cout` : chaque page est `cout.html`, à côté
  d'`index.html`, et ses chemins restent ceux d'aujourd'hui. GitHub Pages sert
  bien `cout.html` à l'adresse `…/cout` (vérifié le 26 octobre 2026 sur
  `…/index`), mais c'est une commodité de GitHub, qu'un autre serveur — celui
  de la copie — n'offre pas forcément sans réglage ; et `…/cout/`, avec la
  barre, y répond 404.

**Recommandation : des dossiers.** C'est la seule forme qui ne demande rien au
serveur de la copie, ce que le document d'intégration promet.

## Ce qu'il faudrait modifier

- *Le routeur.* Il lit la page dans le chemin et le lecteur dans l'ancre, et
  garde la lecture de l'ancienne forme le temps de la redirection. Ses 2 967
  lignes, en ligne dans `index.html` (133 Kio, 43 compressés, sur 142),
  passent dans un module partagé : neuf pages ne les porteront pas chacune, et
  le navigateur ne les chargera qu'une fois.
- *Les liens que les pages écrivent* : `lien` et `route`, dans `gabarit.js`,
  qui écrivent aujourd'hui `#/cout?…`, écriront le chemin de la page,
  relatif à celle où il est posé (`../cout/#…`), et les réglages derrière le
  `#`. Les 55 appels de `pages.js` suivent la fonction sans retouche ; restent
  18 adresses écrites en dur (6 dans `pages.js`, 3 dans `gabarit.js`, 9 dans
  `index.html`), dont le partage, `reprendreLaSaisie` et les formulaires.
- *Les pages* : un `index.html` par dossier — d'abord la même coquille que
  l'accueil, ses chemins d'un niveau plus bas, puis la page pré-rendue.
- *Les tests* : une quarantaine de lignes en `#/` dans huit fichiers, dont 16
  dans `test_web_revues.py` et 9 dans `test_web_saisie.py` ; les 36 lectures du
  routeur dans `index.html` (24 dans `test_web.py`, 12 dans
  `test_web_revues.py`), qui liront son module ; les routes des écrans et de
  la mesure Lighthouse ; et un test de plus pour chaque ancienne forme
  d'adresse, ouverte dans un vrai navigateur.
- *Les témoins* des pages : chaque lien qu'elles écrivent change de forme ; le
  diff ne doit montrer que cela.
- *La documentation* : le document d'intégration (12 adresses citées), la
  carte du dépôt (12), dont `tests/test_carte_du_depot.py` confronte le
  tableau des pages au site et n'y lit que des adresses en `#/`, le parcours
  de présentation (3), que `tests/test_parcours.py` rejoue, le README (2),
  l'architecture (1). Les récits de la feuille de route gardent les
  anciennes, vraies à leur date.

Ni les scripts ni le paquet Python n'écrivent ces adresses. Le dépôt n'a ni
`404.html`, ni `sitemap.xml`, ni `robots.txt` : les deux derniers pourront
suivre, une fois les pages séparées.

## Les risques, et leur parade

- *Une ancienne adresse cassée* : chaque forme connue — page, page et
  réglages, simulation, ancienne simulation sur `#/?…`, les deux pages
  fondues — a son test dans le navigateur, sur l'adresse d'arrivée et sur ce
  que la page montre.
- *Un chemin relatif faux dans une page d'un dossier* : le pilote du navigateur
  ouvrira chaque page à neuf, comme il le fait déjà pour mesurer les
  décalages, et comptera toute ressource en erreur.
- *Une adresse mal tapée* (`…/cuot/`) : GitHub Pages sert la page 404 du
  projet ; une `404.html` du dépôt peut ramener à l'accueil. La copie suit les
  réglages de son serveur.
- *Deux versions du site le temps d'un cache* : GitHub Pages garde dix minutes
  ses fichiers en cache, aujourd'hui déjà ; une page neuve et un module ancien
  peuvent se croiser dans cet intervalle, comme ils le peuvent déjà.
- *La copie mise à jour en retard* : l'ancienne copie garde ses anciennes
  adresses, qui marchent ; la nouvelle les redirige. Il n'y a pas de moment où
  un lien du site du parti ne mène nulle part.

## Comment on reviendrait en arrière

Les commits se défont. Seules les adresses de la nouvelle forme partagées entre
temps (`…/cout/`) en souffriraient : on garderait alors les dossiers, réduits à
une redirection vers l'ancienne forme, le temps qu'il faut.

## L'ordre des travaux

Chaque étape se publie seule, et le site reste entier entre deux.

1. *Le routeur lit les deux formes*, sorti d'`index.html` dans son module ; la
   redirection des anciennes adresses est prête, mais rien ne l'emploie
   encore. Rien ne change pour le lecteur.
2. *Les dossiers des pages*, chacun avec la coquille de l'accueil ; les pages
   écrivent leurs liens sous la nouvelle forme ; l'accueil redirige l'ancienne.
   Le document d'intégration le dit le même jour, et l'hôte en est prévenu.
3. *Le pré-rendu* (étape 4 de l'action), qui remplace chaque coquille par la
   page toute faite.

Les deux premières tiennent chacune dans une session de travail, tests et
témoins compris ; la troisième dépend de la décision 2, et en demandera
davantage.

## Ce que cette décision ne tranche pas

- *Où se fabriquent les pages* (décision 2). Elle touche celle-ci par un point
  : si les pages ne se fabriquent qu'au déploiement, le dépôt ne les contient
  plus, et la copie du site du parti ne peut plus « recopier le dépôt tel
  quel » ; elle devrait se faire depuis le site publié. C'est un argument pour
  commiter les pages.
- *Les résultats d'une simulation* (décision 3).
- *L'adresse que les moteurs de recherche retiennent.* Le même site vit à deux
  adresses, GitHub Pages et la copie ; chaque page pourra dire laquelle fait
  foi (`<link rel="canonical">`), et ce choix revient au propriétaire. Rien ne
  presse : aujourd'hui les moteurs ne voient qu'une page.
