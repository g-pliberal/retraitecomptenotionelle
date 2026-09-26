# Outillage d'audit d'interface — les récits

*Archive, gelée.* Les deux sections de récit de `docs/outillage_interface.md`,
déplacées telles quelles le 26 septembre 2026, à la phase 1 de l'architecture
(`docs/architecture.md`, § 9.3) : ce que le navigateur ne voyait pas hors de
`localhost`, et ce qu'un navigateur ne débloque pas. Le document ne garde que
ce qui vaut aujourd'hui.

## Le navigateur ne voit rien hors de `localhost`, et il le dit mal

Dans une session web, le trafic HTTPS sortant traverse un proxy qui
re-termine TLS : tout outil doit donc faire confiance au certificat de son
autorité. Le fichier `/root/.ccr/README.md` annonce que « le magasin NSS du
navigateur » est déjà préparé. **Le 19 septembre 2026, il était vide**, et
Chromium refusait toute adresse HTTPS avec `ERR_CERT_AUTHORITY_INVALID` —
`example.com` comprise.

Le symptôme trompe, et c'est là qu'on perd du temps. Un audit d'interface
ouvre une page servie en local, sur `http://127.0.0.1`, qui ne passe pas par
le proxy : tout marche. L'échec n'arrive que sur une adresse extérieure, et
une erreur de CERTIFICAT sur un site protégé par un pare-feu anti-robot se
lit spontanément comme un refus du site. C'est ce qui s'est produit : une
session a conclu qu'un site public la bloquait, alors que son navigateur
n'avait jamais établi la connexion.

La correction tient en une ligne, une fois par conteneur :

```bash
apt-get install -y libnss3-tools    # certutil n'est pas dans l'image
certutil -A -n ccr-agent-proxy -t "C,," -d sql:$HOME/.pki/nssdb \
    -i /root/.ccr/agent-proxy-ca.crt
```

Ce n'est pas un contournement : c'est exactement ce que le README prescrit
pour les autres outils, qu'on pointe vers `/root/.ccr/ca-bundle.crt`. Chromium
n'ayant pas d'option de CA, il faut passer par son magasin. **Ne jamais y
substituer `--ignore-certificate-errors` ni `ignoreHTTPSErrors`** : ceux-là
désactivent la vérification au lieu d'ajouter une confiance.

Pour vérifier en trois secondes que le navigateur voit dehors :

```bash
node -e 'import("/opt/node22/lib/node_modules/playwright/index.mjs").then(async ({chromium}) => {
  const n = await chromium.launch(); const p = await n.newPage();
  console.log((await p.goto("https://example.com/")).status()); await n.close(); })'
```

## Ce qu'un navigateur ne débloque pas

Une fois le certificat réglé, Playwright ouvre ce que `curl` ne sait pas
ouvrir : les pages dont le contenu est construit en JavaScript, et celles qui
exigent un vrai moteur de rendu. C'est un gain réel, et il vaut d'essayer
avant de conclure qu'une source est hors de portée.

Il ne débloque pas un **refus délibéré**. `budget.gouv.fr`, qui publie les
annexes budgétaires, répond 403 à Chromium avec une page Incapsula portant un
identifiant d'incident et `NOINDEX, NOFOLLOW` : ce n'est pas un défi que
l'exécution du JavaScript résout, c'est une décision. Passer outre
demanderait de maquiller les signaux d'automatisation du navigateur, ce que
le dépôt ne fait pas. Une source qui refuse se consigne comme limite — voir
le volet H de l'action 37 — plutôt que de se forcer.

Ce refus se consigne à un endroit précis : le champ `blocage` du jeu dans
`data/sources.yaml` — `refus` quand le site repousse la session et laisserait
passer un navigateur ordinaire, `reseau` quand c'est la machine qui ne joint
pas le site, `convention` quand l'accès demande une clé ou un compte. La liste
de ce que le dépôt ne peut pas aller chercher lui-même se lit d'une commande :

```bash
python scripts/fetch/source_locale.py
```

Avant d'apporter quoi que ce soit, **chercher le miroir**. Les annexes
budgétaires que `budget.gouv.fr` refuse sont déposées au Parlement, et
l'Assemblée nationale sert le même fichier, octet pour octet, à une session :
le jaune pensions et les projets annuels de performances du PLF 2026 s'y
téléchargent sans personne. Le manifeste porte cette adresse sous `miroir` et
l'empreinte SHA-256 du document sous `sha256` ; `--recuperer` télécharge chaque
miroir dans `data/brut/` et refuse un fichier dont l'empreinte diffère. C'est
le cas qu'on vise : zéro intervention.

```bash
python scripts/fetch/source_locale.py --recuperer
```

Ce qui n'a pas de miroir public, **le dépôt se le fabrique**. Le workflow
`.github/workflows/documents-apportes.yml` — lancé à la main depuis l'onglet
Actions, et le 3 de chaque mois — exécute `source_locale.py --publier` sur
un runner GitHub : pour chaque jeu `refus` qui vise un fichier et n'a pas
d'autre miroir, il télécharge l'adresse de document (`document` dans le
manifeste quand `url` est une page, sinon `url`), d'abord par une requête
simple sous l'identité du dépôt, puis, si le site la refuse, avec un Chromium
Playwright headless ordinaire, installé seulement à ce moment-là. Rien n'y est
maquillé : ni le User-Agent, qui dit « HeadlessChrome », ni les signaux
d'automatisation. Le site veut un navigateur, en voici un ; il ouvre la page
qui présente le document, clique son lien, ou navigue vers l'adresse. Le
fichier obtenu est déposé sur la release `documents-apportes` du dépôt, l'asset
du même nom remplacé, et le corps de la release reçoit une ligne par document
avec son empreinte SHA-256 et sa date. L'adresse de l'asset devient le `miroir`
du jeu, avec son `sha256`, et `--recuperer` le rapporte dans une session comme
n'importe quel miroir ; tant que le manifeste ne le déclare pas, `--recuperer`
cherche déjà la release et imprime l'empreinte à inscrire. Le jeton d'un
workflow a le droit d'écrire les releases, celui d'une session ne l'a pas : la
publication se fait là, jamais depuis un poste. Une édition qui aurait changé
n'écrase pas l'asset dont le manifeste porte l'empreinte : l'écart est dit, et
le job échoue pour qu'on le lise.

Ce qui refuse **aussi le runner**, on l'apporte, une fois. Le 20 septembre 2026,
le bord Akamai de la Banque de France a répondu 403 « Access Denied » au
runner GitHub comme à la session, à la requête simple comme au Chromium
ordinaire, sur la page du rapport de l'OPEF comme sur son PDF : c'est une
décision sur l'adresse du client, pas un défi qu'un navigateur résout, et le
dépôt ne se déguise pas pour passer. La release `documents-apportes` existe
dès la première passe du workflow, même vide, précisément pour ce cas : le
fichier téléchargé sur un poste ordinaire s'y dépose à la main (onglet
Releases, modifier la release, glisser le fichier), sous le nom que le manifeste
déclare en `fichier_local`. Dès lors, `--recuperer` le rapporte dans toute
session, le workflow le conserve quand le site refuse encore, et le geste ne se
refait pas. Un dépôt dans `data/brut/` d'une session — ou `--fichier CHEMIN`
sur un récupérateur — sert aussi, mais à cette session seule : `data/brut/`
n'est pas versionné, et ce qui est versionné, c'est ce que le récupérateur en
tire, avec les mêmes contrôles qu'après un téléchargement. Au 20 septembre
2026, le rapport de l'OPEF est le seul document dans ce cas ; vie-publique
n'en porte que l'édition 2025.
