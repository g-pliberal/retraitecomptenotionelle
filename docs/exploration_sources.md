# Explorer les sources officielles — la méthode

Le 22 septembre 2026, 260 adresses ont été remises au dépôt en huit lots :
simulateurs de caisses, pages de règles, barèmes, circulaires, index de
documents, et quatre modèles publics dont le code est ouvert. Elles sont
inventoriées dans `data/sources_a_explorer.yaml`, une par ligne, avec ce
qu'on va y chercher. Le chantier est l'action 89 de `docs/feuille_de_route.md`.
Ce document dit comment le mener, parce que la moitié du travail est mécanique
et que la refaire à chaque session coûterait plus cher que les sources.

La consigne qui l'ouvre tient en deux phrases. **Ne pas rester à la surface :**
une adresse d'index mène à trente documents, un simulateur mène à un barème
entier. **Ne pas croire un simulateur sur parole :** ils sont écrits par des
mains humaines, et l'on en a la preuve dans ce dépôt même.

---

## Ce qu'une session obtient, mesuré et non supposé

Les 260 adresses ont été sondées le 22 septembre 2026, à raison d'une requête
chacune. Deux cent cinquante-deux ont répondu 200 du premier coup. Les huit autres
tiennent en cinq cas, et chacun a sa recette — aucune ne consiste à baisser
une vérification.

### `session` — 252 adresses, rien à faire

`curl` suffit, la page arrive. C'est l'immense majorité, et c'est contraire à
ce que le dépôt supposait : `tests/temoins/exemples_officiels.yaml` ouvre sur
« aucun simulateur officiel n'est automatisable », phrase vraie de « Mon
estimation retraite », qui exige FranceConnect, et fausse de la vingtaine de
calculettes anonymes que les mêmes caisses publient à côté.

### `chaine_incomplete` — le certificat auquel il manque un maillon

`*.info-retraite.fr` sert son certificat SANS l'intermédiaire qui le rattache
à la racine. Un navigateur va chercher le maillon manquant tout seul (le
certificat dit où : `Authority Information Access`), `curl` non — il s'arrête
sur « unable to get local issuer certificate », et trois sessions successives
ont pu en conclure que le GIP bloquait les robots. Il ne bloque rien : c'est
son serveur qui est mal configuré.

Le maillon se récupère chez n'importe quel hôte qui, lui, le sert — ici
`espace-personnel.agirc-arrco.fr`, même fédération, même autorité Sectigo —
et se joint au paquet de confiance du proxy :

```bash
D=$TMPDIR/chaine                       # un répertoire de travail quelconque
openssl s_client -connect espace-personnel.agirc-arrco.fr:443 \
    -servername espace-personnel.agirc-arrco.fr \
    -proxy 127.0.0.1:${HTTPS_PROXY##*:} -showcerts </dev/null 2>/dev/null \
  | awk '/BEGIN CERT/{n++} n==2' > $D/intermediaire.pem
cat /root/.ccr/ca-bundle.crt $D/intermediaire.pem > $D/bundle.pem
curl --cacert $D/bundle.pem https://les-simulateurs.info-retraite.fr/
```

La vérification reste ENTIÈRE : on ajoute un maillon signé par une racine déjà
de confiance, on ne dispense de rien. `-k` et `--insecure` n'ont pas leur place
ici, et le proxy le dit aussi (`/root/.ccr/README.md`).

### `navigateur` — Cloudflare, ou une page qui se construit en JavaScript

`crpratp.fr` répond 403 avec la page « Attention Required » de Cloudflare.
Chromium passe, et il est déjà installé : `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`,
sans rien à télécharger. La compétence `playwright-cli` de `.claude/skills/`
le pilote ; `docs/outillage_interface.md` dit ce qu'une machine neuve reçoit.
C'est la même voie pour les simulateurs dont le calcul ne part qu'au clic.

`www.enim.eu` est un cas plus traître : il répond **200** à `curl`, et le
sondage l'a donc rangé en `session`. Mais ces 200 portent une page de 212
octets, un script du pare-feu Incapsula et rien d'autre. Un code de réponse
ne dit pas qu'on a lu la page : il faut regarder sa taille.
`scripts/fetch/sonder_sources.py` refait le sondage en jugeant le CORPS —
taille, marques d'Incapsula et de Cloudflare — et imprime les lignes dont
l'accès déclaré est démenti ; il n'écrit rien. Passé sur les deux cent
soixante adresses le soir du 22 septembre 2026, il a rangé en `navigateur`
les six pages de l'ENIM et trois de mon-entreprise, coquilles de 7 Ko que le
JavaScript remplit. Il a aussi montré son propre piège : Incapsula glisse son
script dans les VRAIES pages qu'il protège — celles de la fonction publique en
portent un au milieu de cinquante kilo-octets de contenu. Une marque ne suffit
donc pas ; c'est le texte visible qui tranche. Chromium passe,
une fois son magasin de certificats préparé comme le dit
`docs/outillage_interface.md` (`certutil`, paquet `libnss3-tools`).

### `git` — la page est refusée, le dépôt ne l'est pas

`github.com` répond 403 en HTML à travers le proxy de sortie, et `git clone`
passe sans un mot (vérifié sur `openfisca-france-pension` et sur
`betagouv/mon-entreprise`). Cloner, puis lire les fichiers : c'est de toute
façon la bonne manière de lire du code.

### `refus` et `ferme` — ce qui ne se contourne pas

Deux cas, et la conduite est la même : le consigner, ne pas insister. Le
premier est un `refus` — l'hôte, ou la politique de sortie, dit non à une
session ; le second est `ferme`, et le défaut est tel qu'aucun client correct
ne doit passer outre.

- `espace-personnel.agirc-arrco.fr` sert un certificat EXPIRÉ. Le défaut est
  chez l'émetteur et se répare de son côté ; aucune session ne doit passer
  outre. À resonder de loin en loin.
- `legifrance.gouv.fr` répond 403, comme `CLAUDE.md` l'annonce depuis
  longtemps. L'index plein texte LEGI du dépôt sert le même contenu :
  `python scripts/fetch/dila_cherche.py legi '...' --num R351-9`.

---

## Un simulateur est un oracle, pas un site à lire

C'est la différence entre ce lot et une bibliographie ordinaire. Une page de
règle donne une phrase ; un simulateur donne une FONCTION, et on peut
l'interroger autant de fois qu'on veut. Vingt appels bien choisis rendent le
barème que la caisse n'a pas publié.

**Trouver l'entrée avant de tout balayer.** Regarder d'abord si le calcul est
dans la page : plusieurs de ces calculettes sont des fichiers HTML autonomes
dont le JavaScript porte les taux en clair — la calculette fiscale de
l'Agirc-Arrco en est une. Le barème est alors lisible directement, sans une
seule exécution. Sinon, voir si le formulaire poste vers un point d'appel qui
rend du JSON : c'est ce qu'on interroge, pas la page. Chromium ne vient qu'en
troisième.

**Balayer une grille, pas des cas au hasard.** Faire varier un paramètre à la
fois, par pas réguliers, et resserrer autour des sauts : un barème par classes
se révèle par ses discontinuités, un coefficient par âge par sa pente. Les
ruptures sont les seuils, et les seuils sont ce qu'on cherche.

**Garder peu, et garder le cru.** Les réponses brutes vont dans le répertoire
de travail de la session, pas dans le dépôt. Ce qui entre, ce sont les
quelques points qui tiennent le barème — trois ou quatre par règle — transcrits
dans `tests/temoins/exemples_officiels.yaml` avec leur date et rejoués par
`tests/test_oracle.py` contre le scénario 1. Un fichier de dix mille lignes
de sortie ne prouve rien de plus et personne ne le relira.

**Un zéro n'est pas un refus.** Trois pages de `juris-cnracl.retraites.fr`
ont rendu un code 000 — pas de réponse du tout — quand les vingt et une autres
du même hôte répondaient : c'était la charge de six requêtes en parallèle, et
les trois sont revenues du premier coup en série. Toujours resonder seul, et
lentement, avant de conclure qu'un site refuse.

**Espacer les requêtes.** Ces serveurs sont ceux d'organismes publics et
personne ne les a prévenus. Un appel par seconde au plus, une session à la
fois sur un même hôte, et l'on garde en cache ce qu'on a déjà demandé.

---

## Ce qu'un simulateur vaut — et ce qu'il ne vaut pas

Un simulateur est une source d'APPLICATION : il dit ce que la caisse fait, et
c'est précisément ce que `docs/veille_droit.md` exige à côté du texte. Il n'est
pas une source de DROIT. Quand les deux se contredisent, le texte l'emporte —
et l'écart lui-même est un résultat, à écrire dans `docs/limites.md`.

Le dépôt sait ce que vaut cette prudence : le 17 septembre 2026, ses propres
âges légaux étaient certifiés, faux, et lus dans un dump antérieur à la loi qui
les avait changés. Ce qui lui est arrivé arrive aux caisses. Quatre défauts
reviennent, et il faut les chercher :

- **Le paramètre resté à l'année passée.** Valeur de point, plafond, taux de
  CSG. Le vérifier sur la page de barème du même organisme.
- **La borne d'âge qui n'a pas suivi la dernière loi.** Le défaut le plus
  probable en ce moment, et le plus coûteux.
- **La calculette gelée à sa date.** `sim2010` de la CNRACL applique le droit
  de 2010. Ce n'est pas un défaut si on le sait : c'est au contraire le seul
  moyen de vérifier le modèle SUR LE PASSÉ. C'en est un si on la prend pour
  le droit d'aujourd'hui.
- **L'arrondi et la saisie muette.** Un champ qui plafonne sans le dire, un
  mois compté comme un douzième d'année. Se repère en donnant une entrée
  extrême et en regardant si la sortie plie.

Et la règle de niveau, qui est celle du manifeste : une valeur lue sur un
simulateur est une transcription, jamais un producteur. Elle plafonne au niveau
`haute`, comme celles d'OpenFisca, et ne devient `certifiee` que confrontée au
texte ou au barème publié. Deux organismes qui disent la même chose sur la
même règle — la CSG des pensions, par exemple, que la Cnav, l'Ircantec,
l'Agirc-Arrco, la CARPIMKO, la CNIEG et service-public décrivent chacun de leur
côté — valent un recoupement, et c'est ce qui fait monter une valeur d'un cran.

---

## Ce que le premier lot a appris

Le lot de l'ENIM, le 22 septembre 2026, a rendu plus que ses six pages, et
quatre de ses leçons valent pour toutes les autres.

- **Lire la fiche d'abord a payé.** C'est en ayant sous les yeux la note qui
  disait « la fiche porte cinquante-cinq, l'âge de jouissance » que l'exemple
  de Gaspard, parti à cinquante ans, a sauté aux yeux. Sans elle, la page se
  lisait comme une description, et rien n'aurait été corrigé.
- **Une page de caisse renvoie au texte, et c'est le texte qui tranche.**
  L'ENIM cite ses articles au bas de chaque page. Les lire dans l'index LEGI a
  pris quelques minutes et a donné trois règles de plus que la page n'en
  disait — la pension spéciale, la levée du plafond, le décompte au semestre.
- **Une page peut se contredire elle-même.** Celle de l'ENIM renvoie à l'âge
  légal du régime général dans son texte, et fait partir son exemple à
  soixante ans trois lignes plus bas. Transcrire l'exemple sans relire le
  texte aurait choisi au hasard.
- **Âge d'ouverture et âge de jouissance ne sont pas la même chose.** La
  fiche des marins portait le second à la place du premier. Toute fiche de
  régime spécial dont l'âge est « fixé pour l'entrée en jouissance » mérite
  la même question : à quel âge le DROIT s'acquiert-il ?

Le lot des professions juridiques, le 23 septembre 2026, en a ajouté deux.

- **Une section libérale écrit ses règles dans des arrêtés, pas dans un
  code.** Les âges, la décote et les majorations de la CAVOM et de la CPRN ne
  sont dans aucun article de l'index LEGI : ils sont dans les statuts, puis
  les règlements, que des arrêtés approuvent et que le Journal officiel
  publie en annexe. `dila_cherche.py jorf 'Arrêté AND statuts AND
  notaires'` les trouve tous, du premier au dernier, et c'est la seule
  façon de dater une règle que la page de la caisse ne décrit qu'au présent.
- **Une fiche qui suit le régime général par défaut se trompe en silence.**
  Trois fiches lisaient les âges des tables communes et laissaient la durée
  annuler leur décote, parce que c'est ce que font les drapeaux par défaut.
  Pour chaque complémentaire de section, poser deux questions : quels âges
  son règlement écrit-il, et la durée d'assurance y annule-t-elle la
  minoration ?

## Où va ce qu'on en tire

Rien ne reste dans un fichier de notes : chaque trouvaille a sa destination,
et c'est la destination qui décide si la trouvaille compte.

| ce qu'on a trouvé | où ça va |
| --- | --- |
| un exemple chiffré complet | `tests/temoins/exemples_officiels.yaml`, rejoué par `tests/test_oracle.py` |
| une règle de droit, lue à sa source | `data/reference/legislation/veille.yaml`, avec sa date et son état |
| une réforme non coupée | `data/reference/legislation/reformes.yaml` |
| un barème, une valeur, une série | `data/reference/regimes/`, et la source passe à `data/sources.yaml` |
| une règle que le dépôt n'applique pas | `docs/limites.md`, et la fiche du régime |
| une source qui a tout rendu | son `statut: epuise` et sa date dans `sources_a_explorer.yaml` |

`data/sources_a_explorer.yaml` est un SAS, pas une bibliothèque : une source y
entre repérée et en sort épuisée. Le manifeste `data/sources.yaml` ne porte que
ce qui a déjà donné une valeur ; tant qu'une adresse n'a rien donné, elle reste
ici.

---

## Comment une session prend sa part

Le lot ne se traite pas d'un coup, et il ne faut pas essayer : 260 adresses,
dont vingt-huit simulateurs à balayer, valent plusieurs journées. La
manière de s'y prendre est celle que `CLAUDE.md` impose déjà pour les sessions
parallèles — par zone, et en poussant souvent.

1. Prendre un LOT COHÉRENT : un régime, ou une famille (les sections libérales,
   les régimes spéciaux, le versant international, les modèles publics).
   Ne pas piocher au hasard dans la liste.
   Puis LE RÉSERVER : passer ses lignes à `en_cours` et pousser ce seul
   commit, avant d'ouvrir une source. Le 22 septembre 2026, deux sessions ont
   pris le lot de l'IRCEC le même soir, chacune sur un `main` où il était
   encore `a_explorer` ; la seconde a lu les mêmes règlements et écrit le
   même barème, et n'a découvert la première qu'en poussant.
2. Lire la fiche du régime concerné avant d'ouvrir la source : on cherche ce
   qui MANQUE, pas ce qu'on a déjà. L'inventaire dit lesquelles sont
   `partiel`, et le champ `a_en_tirer` de chaque ligne dit quoi y chercher.
3. Dépouiller, transcrire selon le tableau ci-dessus, passer la ligne à
   `explore` ou `epuise` avec sa date, et écrire dans la note ce qu'on a
   trouvé — ou ce qui a arrêté.
4. Si le scénario 1 est touché : `python scripts/veille_droit.py` en
   commençant, une ligne au `journal` de `veille.yaml` en finissant. C'est
   une obligation, pas un usage.
5. Commiter petit, pousser souvent : `python -m pytest`, puis
   `bash scripts/pousser.sh`. Écrire dans la feuille de route au dernier
   commit, jamais au premier.

Ce que la session suivante doit trouver en arrivant : l'inventaire à jour, et
assez de notes pour n'avoir pas à rouvrir ce qu'on a déjà ouvert.
