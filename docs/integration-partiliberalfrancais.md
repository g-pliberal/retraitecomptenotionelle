# Le simulateur sous partiliberalfrancais.fr/retraite/ — ce que l'hôte doit savoir

Ce fichier est la remise au mainteneur du site partiliberalfrancais.fr. Il dit
qui contrôle quoi, ce qui a été observé sur le site en production, les adresses
stables du simulateur, ce qu'il attend d'un hébergement, et la plus petite
intégration qui suffise. Tout ce qui décrit le site parent y est daté : ce site
évolue sans que ce dépôt le sache, et rien ici ne doit être lu comme une
promesse sur son état futur.

## La frontière

- **Ce dépôt** contrôle l'application de retraite : `index.html`, `moteur/`,
  les données et le modèle. Il la publie tel quel sur GitHub Pages
  (`g-pliberal.github.io/retraitecomptenotionelle/`).
- **Le site partiliberalfrancais.fr** n'est pas contrôlé d'ici. Ni son HTML,
  ni ses feuilles, ni ses scripts, ni sa configuration de serveur. Il est
  traité en lecture seule ; il n'a été ni modifié, ni déployé par le travail
  qui a produit ce fichier.
- Le simulateur **ne charge rien** du site parent — ni feuille, ni police, ni
  script, ni image — et ne dépend d'aucune de ses classes, d'aucun de ses
  fichiers, d'aucune de ses adresses hormis sa racine, qu'il lie.

## Ce qui a été observé le 17 septembre 2026

Lu dans le navigateur et par requête directe ; à revérifier avant de s'y fier.

| | Observé |
|---|---|
| Site parent | `https://partiliberalfrancais.fr/` — page unique, Bootstrap, onglets « pills » routés par `#`, fond dégradé bleu-vert, texte blanc, titres en police de marque, liens turquoise, focus doré. |
| Simulateur | `https://partiliberalfrancais.fr/retraite/` — une **copie** de ce dépôt, servie par le même hébergeur que le site (mêmes en-têtes, même `last-modified`), pas un proxy vers GitHub Pages. La copie datait d'un commit **antérieur** à `main` (le script de `index.html` y manquait deux blocs plus récents). |
| Modifications de la copie | Deux, faites côté hôte dans `index.html` : une feuille `plf-theme.css` chargée **après** `moteur/style.css`, et un bandeau `<div class="plf-back-link">Simulateur du Parti Libéral Français — retour au site</div>` inséré en tête de `<body>`. |
| Ce que fait `plf-theme.css` | Redéfinit dans un seul `:root` toutes les variables de couleur du simulateur (thème sombre imposé quelle que soit la préférence système), la police du corps et des titres (dont une `@font-face` du site), le style des boutons, et impose un plancher de 1 rem à une vingtaine de sélecteurs **internes** du simulateur (`.metier > .rang`, `.scenario .chiffre .unite`, `thead th`…). |
| Point d'entrée sur le site | L'onglet « Retraites notionnelles » (`/#simulateur`) existe mais est **masqué** (`display:none` sur son `<li>`, commentaire : « pas encore prêt pour le public »). L'adresse `/#simulateur` fonctionne si on la tape : elle ouvre un panneau qui contient une `<iframe>` chargée à la demande sur `/retraite/`. |
| Comportement de l'iframe | Le script `/js/embedded-frames.js` du site, même origine, pose la classe `plf-embedded` sur le `<body>` du simulateur (ce qui masque, via `plf-theme.css`, le bandeau de retour et le titre), puis remesure la hauteur du corps toutes les 500 ms pour ajuster le cadre. |
| Seul lien visible vers le simulateur | Aucun dans la navigation. Une balise `<noscript>` du panneau masqué porte `<a href="/retraite/">`. |
| En-têtes HTTP | Ni `Content-Security-Policy`, ni `X-Frame-Options`, ni `frame-ancestors` sur `/` ni sur `/retraite/`. `cache-control: no-cache`, `etag`, HSTS. `/retraite` sans barre redirige en 301 vers `/retraite/`. |
| Chemins relatifs | `moteur/style.css`, `moteur/donnees.json`, `moteur/js/*.js` répondent 200 sous `/retraite/` ; la page se charge et calcule (six scénarios sur une adresse paramétrée). |
| Avant JavaScript | L'écran d'attente de ce dépôt, sous le thème de l'hôte ; sans script, le `<noscript>` du simulateur explique qu'il faut JavaScript. |

Deux conséquences de cette intégration, telles qu'elle était ce jour-là :

1. **Elle dépend de l'intérieur du simulateur.** `plf-theme.css` cite des
   sélecteurs que ce dépôt ne s'est jamais engagé à garder. Chaque mise à
   jour de la copie peut en casser une partie sans que rien ne le signale.
2. **Elle impose le thème sombre aux deux préférences système**, et remplace
   une palette dont les contrastes sont mesurés par des tests par une palette
   mesurée à part. C'était une réponse raisonnable au fait que le simulateur
   ne ressemblait pas au site. Ce n'est plus nécessaire : voir plus bas.

## Les adresses stables

Le simulateur tient dans une seule page ; tout ce qui suit `#` est traité dans
le navigateur, aucune route n'a besoin d'être configurée côté serveur.

| Adresse | Ce qu'elle montre |
|---|---|
| `/retraite/` | L'accueil : le programme, puis les liens vers les cinq autres pages. |
| `/retraite/#/simuler` | Le formulaire de simulation, vide de tout résultat. |
| `/retraite/#/simuler?…` | Une simulation, tous paramètres dans l'adresse : elle se partage, se cite, se recharge. Exemple : `#/simuler?naissance=1965-03-01&sexe=H&statut=salarie_prive_non_cadre&debut=1985-09-01&liquidation=2029-03-01`. |
| `/retraite/#/cas-types`, `#/cout`, `#/methode`, `#/donnees` | Les autres pages. |

Ces adresses sont celles que les pages du simulateur écrivent elles-mêmes ;
elles ne changeront pas sans que ce fichier le dise. Les anciennes adresses de
simulation sur `#/?…` restent lues.

### Quel lien poser : `/retraite/` ou `/retraite/#/simuler` ?

Une analyse d'usage, pas un avis sur le fond.

| | `/retraite/` | `/retraite/#/simuler` |
|---|---|---|
| Ce qu'on voit | Le programme (proposition, trois chiffres, quatre idées, le plancher), la navigation vers Simuler | Le formulaire, cinq champs préremplis, le bouton « Calculer les six scénarios » |
| Gestes avant un premier résultat | Deux : cliquer « Simuler », puis « Calculer » (ou ajuster puis calculer) | Un : « Calculer » — ou ajuster puis calculer |
| Contexte perdu en arrivant direct sur le formulaire | Aucun de nécessaire : le formulaire est autonome, chaque champ porte son aide, et « Programme » reste dans le bandeau, à un clic | — |
| Correspond littéralement à un lien nommé « simulateur » | Non : c'est une page de programme qui mène au simulateur | Oui |

**Recommandation** : un lien libellé « simulateur » pointe sur
`/retraite/#/simuler` ; un lien libellé « notre programme pour les retraites »
ou « retraites notionnelles » pointe sur `/retraite/`. Les deux sont stables,
et les deux pages mènent l'une à l'autre en un clic.

## Ce que le simulateur attend d'un hébergement

Vérifié sur la copie en production et sur GitHub Pages.

- **Des fichiers statiques, servis tels quels**, depuis un répertoire : le
  contenu de ce dépôt, sans transformation. Pas de serveur de calcul, pas de
  base, pas d'API : le modèle tourne dans le navigateur.
- **Les chemins relatifs conservés** : `index.html` charge `moteur/style.css`,
  `moteur/donnees.json` (<!--chiffre:poids(moteur/donnees.json)-->3 056<!--/--> Ko bruts,
  <!--chiffre:poids_comprime(moteur/donnees.json)-->349<!--/--> Ko compressés) et `moteur/js/*.js`
  relativement à sa propre adresse. Le répertoire peut s'appeler autrement que
  `retraite` ; il doit être servi avec sa barre finale (ou rediriger vers
  elle), sinon les chemins relatifs se résolvent un niveau trop haut.
- **Les types MIME usuels** : `text/html`, `text/css`, `application/json`,
  `text/javascript` pour les modules ES.
- **JavaScript activé**, modules ES et `fetch` : tout navigateur de ces cinq
  dernières années. Sans script, la page dit pourquoi elle ne calcule pas.
- **Aucune règle de réécriture** : le routage passe par `#`.
- **La compression** (`gzip` ou `brotli`) est souhaitable pour `donnees.json`,
  pas requise.
- Aucun en-tête particulier n'est requis. Une `Content-Security-Policy`, si
  le site en pose une un jour, doit autoriser `'self'` pour les scripts, les
  styles, les images (`data:` n'est pas utilisé) et `connect-src` — le
  simulateur ne parle à aucune autre origine. Le style de l'écran d'attente
  est **en ligne** dans `index.html` (`<style>`) : une CSP sans
  `'unsafe-inline'` pour les styles le neutraliserait, sans casser le reste.

## Ce que le simulateur charge à l'exécution

Rien qui ne soit dans son propre répertoire : sa feuille, son paquet de
données, ses modules. Aucun CDN, aucune police web, aucun script tiers,
aucune mesure d'audience ; un test du dépôt le vérifie
(`test_la_page_ne_depend_d_aucun_service_exterieur`). Les seules adresses
extérieures sont des **liens** que le lecteur suit s'il le veut : le site
parent, le dépôt GitHub, info-retraite.fr, la licence Creative Commons.

## Données personnelles

Tout est calculé dans le navigateur. Ce qui est saisi — dates, statuts,
revenus, relevé de carrière — ne quitte pas la machine du lecteur ; il
n'existe aucun serveur à qui l'envoyer. Les paramètres sont écrits dans
l'adresse (`#/simuler?…`), donc dans l'historique du navigateur et dans tout
lien partagé, et le fragment `#…` n'est **pas** transmis au serveur par le
navigateur. L'hébergeur voit passer la visite, comme pour toute page.

Le simulateur ne porte **aucune mention légale** : ni identification de
l'éditeur, ni politique de données personnelles, ni déclaration
d'accessibilité. Il portait les trois jusqu'au 18 septembre 2026 ; elles ont
été retirées parce que le site d'accueil édite et héberge la page et porte donc
les siennes, et parce que deux déclarations concurrentes valent moins qu'une —
celle du simulateur nommait GitHub, Inc. comme hébergeur, ce qui n'est vrai que
de l'adresse GitHub Pages.

**C'est donc à l'éditeur du site d'accueil de les porter**, et elles doivent
couvrir `/retraite/` : l'identification de l'éditeur (loi n° 2004-575 du
21 juin 2004, article 6-III), ce que le simulateur fait des données saisies —
rien, comme décrit ci-dessus — et l'état d'accessibilité. Ce que le dépôt
continue de porter, parce que lui seul le connaît, est sa licence : code sous
Apache 2.0, infographies et textes sous CC BY-SA 4.0, séries à citer chez leur
producteur ; c'est en pied de page et sous `#/donnees`, section « Licences et
réutilisation ».

Une conséquence à peser : l'adresse GitHub Pages
(`g-pliberal.github.io/retraitecomptenotionelle/`) n'a pas de site parent pour
porter cette partie légale. Elle est une publication de travail du dépôt ; si
elle doit rester une adresse publique, ses mentions sont à poser ailleurs
(dépôt, `README`) ou l'adresse à fermer.

## L'intégration recommandée : un lien

La plus petite intégration qui suffise, et la plus robuste :

```html
<a href="/retraite/#/simuler">Simuler ma retraite</a>
```

ou, pour le programme, `<a href="/retraite/">Retraites notionnelles</a>`.

C'est tout. Le simulateur porte lui-même, depuis le 17 septembre 2026, ce qui
faisait l'objet des deux modifications côté hôte :

- **Le retour au site.** Une ligne en pied de chaque page, « Un outil du
  Parti libéral français ». Elle porte `target="_top"` : dans un cadre, elle
  ressort du cadre au lieu d'ouvrir le site dedans ; hors cadre, l'attribut ne
  change rien. Le bandeau de tête, lui, ne renvoie plus au site depuis le
  20 septembre 2026 : il tient sur une rangée, le nom du simulateur et ses
  onglets, et le pied suffit pour dire d'où l'on vient. **Le bandeau
  `plf-back-link` inséré par l'hôte fait désormais doublon et peut être
  retiré.**
- **L'air de famille.** Bandeau sombre bleu-vert souligné d'or, accent de la
  même teinte, pile de polices du système : le simulateur ressemble au site
  sans rien lui emprunter. **La feuille `plf-theme.css` n'est plus nécessaire**,
  et ce qu'elle impose (thème sombre forcé, sélecteurs internes) est ce qui
  cassera à la prochaine mise à jour. Si l'hôte tient à ajuster une couleur,
  voir « Le contrat visuel ».

Mettre à jour la copie revient à recopier le dépôt tel quel, sans rien y
changer. Le mieux est de copier une version taguée ou un commit précis de
`main`, et de noter lequel.

### L'iframe, en option

Le site ouvre aujourd'hui le simulateur dans un cadre, sur `/#simulateur`.
Cela fonctionne, et le simulateur n'a rien à faire de particulier pour cela ;
vérifié le 17 septembre 2026 : le cadre se charge, se redimensionne, le
routage par `#` du simulateur ne touche pas celui du site.

Ce qui est garanti côté simulateur si l'hôte garde ce mode :

- **`body.plf-embedded`** : quand l'hôte pose cette classe (même origine), le
  simulateur masque lui-même sa ligne de retour en pied — c'est la seule chose
  qu'il sache de son hôte, et elle ne coûte rien si l'hôte cesse de la poser.
  Le bandeau de tête reste tel quel : il ne porte rien du site, et le titre de
  la page dit quelle page du simulateur est ouverte.
- Le lien de retour ressort du cadre (`target="_top"`).
- **Le défilement après un clic.** Dans un cadre de même origine, le
  simulateur règle lui-même la hauteur du cadre à chaque rendu, puis fait
  défiler la page hôte : jusqu'aux résultats après « Calculer », jusqu'au haut
  du cadre après un changement de page. Sans cela, mesuré le 17 septembre 2026
  sur le site : « Calculer » laissait le lecteur sur le haut du formulaire,
  sans un résultat en vue, parce que le cadre gardait la hauteur de la page
  d'avant jusqu'à la remesure suivante ; et le bouton du bas du programme le
  laissait sur la fin du formulaire et le pied du site. La remesure
  périodique de l'hôte reste utile pour les sections dépliées, et n'entre pas
  en conflit : elle mesure la même chose. Depuis une autre origine,
  `frameElement` est nul et le simulateur fait défiler son propre document,
  comme hors cadre.
- Aucun en-tête `X-Frame-Options` ni `frame-ancestors` n'est posé par le
  dépôt ; c'est à l'hébergeur d'en poser un s'il veut interdire les autres
  origines.

Ce qui reste à la charge de l'hôte, et n'est pas garanti d'ici : la mesure de
hauteur quand une section est dépliée (le simulateur grandit sans que rien ne
soit rendu), et la synchronisation de l'adresse (une simulation faite dans le
cadre n'est pas dans la barre d'adresse du site, donc pas partageable depuis
là). Pour ces deux raisons, **le lien simple est préférable au cadre** ; le
cadre reste supporté.

Ce que le lecteur voit en arrivant par `/#simulateur`, l'hôte masquant le
titre du simulateur : la navigation du simulateur, puis « Notre programme
pour les retraites », son chapeau, et un bloc d'entrée — « Simulez votre
carrière », un bouton « Simuler ma retraite ». C'est ce bloc qui dit qu'il
s'agit d'un simulateur ; il tient dans le premier écran d'un téléphone.

Ce qui n'existe pas, et n'a pas été inventé : de paramètre `?embed=`, de
`postMessage`, de script partagé. Si un jour l'hôte en a besoin, c'est un
contrat à écrire ici d'abord.

## Le contrat visuel

Ce que l'hôte peut compter comme stable, et ce qu'il n'a pas besoin de
connaître.

Stable :

- **La largeur de contenu** : environ 60 rem (960 px), centrée, avec 1,25 rem
  de marge latérale ; la page tient sans défilement horizontal de 320 px à
  1 440 px.
- **Le bandeau** : sombre bleu-vert, souligné d'or, le même en thème clair et
  sombre ; il porte le lien vers le site, le titre du simulateur et sa
  navigation interne. Le simulateur suit la préférence clair/sombre du
  système pour tout le reste.
- **L'accent** : une teinte bleu-vert, assombrie en clair, éclaircie en
  sombre, sur les liens, les boutons et le focus.
- **Les variables de couleur** de `:root` dans `moteur/style.css` : `--fond`,
  `--fond-carte`, `--fond-appui`, `--texte`, `--texte-doux`, `--trait`,
  `--trait-champ`, `--accent`, `--accent-doux`, `--bandeau`,
  `--bandeau-texte`, `--bandeau-doux`, `--bandeau-vif`, `--or`, `--alerte`,
  les six couleurs de scénario et les neuf de série. Leurs **noms** sont
  stables ; leurs valeurs peuvent bouger. Un hôte qui tient absolument à
  ajuster une couleur les redéfinit dans une feuille chargée après, et ne
  touche à rien d'autre. Le thème sombre du simulateur les redéfinit sous
  `@media (prefers-color-scheme: dark)` : une redéfinition faite sans cette
  requête média s'applique aux deux thèmes — c'est le piège dans lequel
  `plf-theme.css` est déjà tombé, et la raison pour laquelle il vaut mieux ne
  rien redéfinir du tout.

Ce que l'hôte n'a **pas** besoin de connaître, et ne doit pas citer :

- les chemins des modules, les noms de fichiers sous `moteur/` ;
- les classes CSS et la structure du HTML rendu (`header.bandeau`,
  `.scenario`, `.metier > .rang`… tout cela peut changer) ;
- le modèle, les données, leur format ;
- la façon dont `moteur/style.css` et `moteur/donnees.json` sont produits.

## Liste de vérification après une mise à jour de la copie

À faire depuis un navigateur ordinaire, sur le site, en cinq minutes.

1. `/retraite/` s'ouvre, affiche le programme, et le pied de page porte le
   lien « Parti libéral français » qui ramène à la racine du site. Le bandeau
   de tête tient sur une rangée au large : le nom du simulateur, puis les
   neuf onglets.
2. `/retraite/#/simuler` ouvre le formulaire ; « Calculer les six scénarios »
   affiche six montants et fait défiler jusqu'à eux.
3. L'adresse d'exemple ci-dessus, collée dans la barre, affiche six scénarios
   sans passer par le formulaire ; recharger la page les réaffiche ; le bouton
   « précédent » du navigateur revient au formulaire.
4. Sur un téléphone (ou une fenêtre de 390 px) : pas de défilement
   horizontal, la navigation tient sous le titre.
5. La console du navigateur ne montre **aucune** requête vers une autre
   origine que le site.
6. En thème sombre du système, la page est sombre ; en clair, claire ; le
   bandeau est le même dans les deux cas.
7. Si `/#simulateur` est encore un cadre : le simulateur s'y affiche sans sa
   ligne de retour en pied, et le titre « Retraite à comptes notionnels »
   reste lisible.
8. Aucun fichier de ce dépôt n'a été modifié dans la copie ; s'il en reste un
   (`plf-theme.css`, `plf-back-link`), il est signalé comme dette dans ce
   fichier.
