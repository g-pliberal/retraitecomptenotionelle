# Le diagnostic Lighthouse des dix routes du site

**Le 25 octobre 2026, la demande.** Le propriétaire : « Je veux que toutes
les pages aient un score maximal dans toutes les catégories lighthouse. On
commence par un diagnostic de toutes les pages. »

**La mesure.** Lighthouse 13.5.0, par `npx`, hors du dépôt, avec le Chromium
des sessions, contre le site en ligne, construit de bdb3b9b. Les dix routes de
`tests/test_ecrans.py` : les neuf pages de `TITRES`, et `RESULTATS`, le
formulaire calculé tel qu'il s'ouvre. Deux profils : mobile, celui par défaut
(réseau simulé à 150 ms et 1,6 Mbit/s, processeur ralenti quatre fois), et
bureau (`--preset=desktop`) ; deux passages de chacun. Lighthouse 13 note cinq
catégories : Performance, Accessibilité, Bonnes pratiques, SEO, et « Agentic
Browsing », neuve et dite « en développement », dont la note tient, à parts
égales, à deux audits : l'arbre d'accessibilité et le CLS.

**Les notes.** Un écart entre les deux passages s'écrit 35–59 ; les temps sont
ceux du premier passage ; le TBT est nul partout.

| Mobile | Perf. | Access. | B. P. | SEO | Agentic | FCP | LCP | CLS |
|---|---|---|---|---|---|---|---|---|
| accueil | 35 | 100 | 100 | 100 | 51 | 6,4 s | 10,6 s | 1,00 |
| simuler | 35 | 100 | 100 | 100 | 51 | 6,3 s | 10,5 s | 1,01 |
| résultats | 59 | 97 | 100 | 100 | 100 | 6,3 s | 10,5 s | 0,01 |
| cout | 35–59 | 98 | 100 | 100 | 1–50 | 6,3 s | 10,5 s | 0–1,01 |
| risque | 35–59 | 99 | 100 | 100 | 51–100 | 6,4 s | 10,6 s | 0–1,01 |
| partager | 35–59 | 100 | 100 | 100 | 51–100 | 6,3 s | 10,5 s | 0,03–1,03 |
| saviez-vous | 35 | 100 | 100 | 100 | 51 | 6,4 s | 10,6 s | 1,02 |
| cas-types | 35–59 | 99 | 100 | 100 | 51–100 | 6,7 s | 10,9 s | 0–1,13 |
| avantages | 35–59 | 99 | 100 | 100 | 1–50 | 6,3 s | 10,5 s | 0,01–1,01 |
| methode | 35–59 | 98 | 100 | 100 | 51–100 | 6,5 s | 10,7 s | 0,03–1,03 |

| Bureau | Perf. | Access. | B. P. | SEO | Agentic | FCP | LCP | CLS |
|---|---|---|---|---|---|---|---|---|
| accueil | 65–66 | 100 | 100 | 100 | 51 | 1,1 s | 1,8 s | 0,96 |
| simuler | 64–65 | 100 | 100 | 100 | 51 | 1,2 s | 1,9 s | 0,96 |
| résultats | 63–64 | 97 | 100 | 100 | 51 | 1,2 s | 1,8 s | 0,96 |
| cout | 65 | 98 | 100 | 100 | 1 | 1,1 s | 1,8 s | 0,97 |
| risque | 65 | 99 | 100 | 100 | 51 | 1,2 s | 1,8 s | 0,96 |
| partager | 64–65 | 100 | 100 | 100 | 51 | 1,2 s | 1,9 s | 0,97 |
| saviez-vous | 65 | 100 | 100 | 100 | 51 | 1,2 s | 1,8 s | 0,96 |
| cas-types | 65 | 99 | 100 | 100 | 51 | 1,1 s | 1,8 s | 1,05 |
| avantages | 65–66 | 99 | 100 | 100 | 1 | 1,1 s | 1,8 s | 0,96 |
| methode | 65 | 98 | 100 | 100 | 51 | 1,2 s | 1,8 s | 0,98 |

**Bonnes pratiques et SEO : 100 partout.** Rien à y faire.

**Les causes, de la plus chère à la moins chère.**

- *Rien ne se peint avant le moteur : FCP 6,3 s et LCP 10,5 s en mobile,
  1,1 et 1,8 s en bureau.* Chaque route télécharge le même 1 923 Kio
  compressés avant d'afficher quoi que ce soit : 74 modules (961 Kio, dont
  `pages.js`, 264 Kio compressés pour 854 bruts), `donnees.json` (832 Kio
  pour 5,7 Mo bruts), la feuille de style et `index.html`. Le premier rendu
  que Chrome compte arrive à 1,15 s sans bridage, avec la page calculée :
  l'écran d'attente, qui naît transparent (`#amorce`, animation `paraitre`,
  retard de 0,35 s, `index.html:109`), ne compte pas. Lantern, qui rejoue le
  chargement sur le réseau simulé, tient alors pour bloquant tout script de
  haute priorité demandé avant ce rendu : les 74 modules, que les
  `modulepreload` de l'en-tête (`index.html:28-101`) demandent tous en haute
  priorité. Le bridage fait le reste : 1,9 Mo à 1,6 Mbit/s, c'est près de dix
  secondes.
- *L'en-tête qui pousse la page : un CLS proche de 1, soit 25 points de
  Performance et la moitié d'Agentic.* `coquille()` (`index.html:216`) pose
  un `#entete` vide au-dessus de `<main>`, où `afficher()` peint l'écran
  d'attente ; le calcul fait, l'en-tête se remplit (`index.html:453`), et tout
  `<main>` descend de 112 à 132 points, un décalage de 0,96 à 1,0 à lui seul.
  En bureau à chaque passage ; en mobile selon le minutage, la moitié des
  routes, pas les mêmes d'un passage à l'autre. S'y ajoute la bascule de la
  police Instrument Serif (`font-display: swap`, `moteur/style.css:45`), de
  0,004 à 0,089 (cas-types, en bureau).
- *Le TBT nul est un sursis.* Le fil principal travaille 2 à 3 s en mobile
  (7,7 s sur les résultats, dont 5 s de JavaScript), mais avant le premier
  rendu, hors de la fenêtre où le TBT se compte. Qu'une page se peigne
  d'abord, et ce travail y tombe : le TBT pèse 30 points, et le moteur ne
  pourra plus se charger au démarrage sur le fil principal.
- *Accessibilité : deux règles.* L'ordre des titres (`heading-order`, poids 3),
  sur cout, risque, cas-types, avantages et methode : le `<h1>` de l'affiche
  est suivi de `<h3>`, sans `<h2>` entre eux (`section#cout-bilan > h3`,
  `section#risque-prelevement > h3`, `div.panneaux > div.panneau > h3`,
  `section#avantages-frise > h3`, `div.points > div.point > h3`). Le contraste
  (`color-contrast`, poids 7), sur les résultats : l'écart des cartes
  (`div.entete > span.montant > span.chiffre > span.ecart`), en `--manque`
  (#e8807f, `moteur/style.css:147`) sur #0f4a46, rend 3,74:1 pour 4,5 exigés
  à 13 px gras.
- *Agentic : un rôle que l'arbre refuse.* L'audit de l'arbre d'accessibilité,
  binaire, échoue sur cout et avantages : une `<figure role="group">` qui
  porte sa légende en `<figcaption>` (règle `aria-allowed-role` d'axe, « ARIA
  role group is not allowed for given element ») — `figure.graphique`
  (`moteur/js/gabarit.js:1668`, sa légende `:2500`) et `figure.sankey`
  (`:2464`). La même règle ne pèse rien dans la catégorie Accessibilité, où
  elle n'est qu'informative. Le même assemblage se retrouve dans la frise
  (`:1910`) et la cascade (`:2121`).
- *Ce qui ne pèse rien.* Lighthouse 13 ne note que les cinq métriques ; ses
  pistes ne comptent pas : la durée de cache (957 Kio, le `max-age=600` de
  GitHub Pages, qu'on ne règle pas), le JavaScript et la feuille non minifiés
  (411 et 21 Kio), le JavaScript inutilisé (300 Kio environ). Ni les cartes de
  source absentes (Bonnes pratiques), ni le formulaire sans annotation WebMCP
  (Agentic), qui sont informatifs, ni `llms.txt`, non applicable.

**Les seuils de 100.** La note de Performance s'arrondit : 100 demande 0,995.
Chaque métrique à 0,995, d'après les courbes de Lighthouse : en mobile, FCP
1,08 s, LCP 1,56 s, TBT 66 ms, CLS 0,040, Speed Index 1,97 s ; en bureau, FCP
0,54 s, LCP 0,60 s, TBT 64 ms, CLS 0,040, Speed Index 0,74 s. Une note de 100
tolère un peu moins sur une métrique quand les autres sont pleines.

**Ce que vaudrait une page pré-rendue.** L'accueil, le simulateur, le coût et
la méthode, rendus par le site en ligne à 412 et à 1 350 points de large, puis
figés sans script ni préchargement — même feuille de style, mêmes polices —,
servis d'ici compressés, en HTTPS et HTTP/2 comme GitHub Pages :

| Page figée | Mobile | Mobile, feuille intégrée | Bureau (HTTP) |
|---|---|---|---|
| accueil | 100 | 100 | 100 |
| simuler | 100 | 100 | 100 |
| cout | 98 | 99 | 100 |
| methode | 99 | 100 | 100 |

En mobile, le FCP tombe à 1,4–1,8 s, le LCP avec lui. Ce qui manque à cout
vient du poids de son HTML (87 Kio compressés, 638 bruts) et de la bascule de
police (CLS 0,03). Un serveur local répond en 15 ms, GitHub Pages en 80 : la
marge réelle est plus mince. Le pré-rendu ne corrige ni l'Accessibilité ni
l'arbre d'Agentic : cout y garde 98 et 50.

**Les résultats d'une simulation.** C'est la seule route dont le contenu
n'existe pas avant le calcul : il lui faut le moteur, 1,8 Mo compressés de
scripts et de données, que le profil mobile met près de neuf secondes à
télécharger et le bureau 1,5 s, quand le LCP n'en permet que 1,6 et 0,6. Tant
que le modèle tourne chez le lecteur — le site le promet : « rien n'est envoyé
à un serveur » —, sa Performance n'atteindra pas 100. Elle peut gagner un CLS
nul, un TBT nul si le calcul passe dans un Web Worker, et ce que retirerait un
paquet coupé par usage : `regimes` pèse 189 Kio compressés sur 808 pour un ou
deux régimes servis, les tables de mortalité 234 pour une génération. Ses
quatre autres notes peuvent atteindre 100.

**Ce qu'il faut, dans l'ordre.**

1. *Le diagnostic* : cette note.
2. *Les défauts sans architecture*, chacun par son test d'abord : l'en-tête
   posé avec `<main>`, avant tout écran d'attente ; la police de titre sans
   bascule visible (une police de repli à ses métriques, `size-adjust`) ;
   l'ordre des titres ; le contraste de l'écart ; le rôle des figures
   légendées. Attendu : Accessibilité et Agentic à 100 sur les dix routes,
   Performance vers 59 en mobile et 90 en bureau, le CLS seul levé.
3. *La mesure au dépôt* : un script qui rejoue ces audits, Lighthouse par
   `npx` et hors des dépendances, comme l'outillage de
   `docs/outillage_interface.md` ; dans la suite, les gardes qui n'en ont pas
   besoin — les règles d'axe trouvées ici, sur les témoins, et le CLS, dans
   `tests/test_ecrans.py`.
4. *Le pré-rendu* : chaque page en HTML statique à sa propre adresse, en-tête
   et pied compris ; ses graphiques et ses tableaux tenus à toute largeur sans
   script — ils se dessinent aujourd'hui à la largeur de la colonne, et
   `plierLesTableaux` replie les tableaux après coup, deux décalages en
   puissance — ; le moteur sorti de l'en-tête, sans `modulepreload` ni
   `preload` au démarrage.
5. *Le moteur à la demande* : au premier geste qui calcule, ou dans un Web
   Worker après le chargement, pour que son travail ne tombe pas dans le TBT ;
   les pages qui recalculent sur place, comme les bascules du coût, l'appellent
   alors.
6. *Les résultats* : ce que le paragraphe précédent dit possible.

**Ce que le propriétaire tranche.**

1. *Les adresses.* Le pré-rendu demande une adresse par page, `…/cout/` au
   lieu de `…/#/cout` : le serveur ne voit jamais ce qui suit `#`, et sert la
   même page à toutes. Les anciennes adresses resteraient valides par une
   redirection, partages et lien du site parent compris (`ADRESSE_SITE`,
   `moteur/js/gabarit.js:45`).
2. *Où se fabriquent les pages* : commitées par la fabrique, comme
   `donnees.json`, sans toucher de garde ; ou faites au déploiement, dans
   `tests.yml`, qui en est une (`Garde-modifiée:`).
3. *Les résultats* : accepter que leur Performance reste sous 100, ou payer le
   découpage du paquet et des scripts pour s'en approcher.

**Refaire la mesure.** Une route prend quinze secondes :

```
npm install --prefix <dossier> lighthouse@13.5.0
CHROME_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome \
  <dossier>/node_modules/.bin/lighthouse \
  'https://g-pliberal.github.io/retraitecomptenotionelle/#/cout' \
  --chrome-flags="--headless=new --no-sandbox" \
  --output=json --output-path=cout.json
```

et `--preset=desktop` pour le bureau. Une session qui en lance plusieurs les
lance l'une après l'autre : en parallèle, leurs mesures se gênent.

**Fichiers.** Cette note et l'action 174 de la feuille de route. Ni code, ni
témoin, ni page, ni journal de veille : le scénario 1 n'est pas touché.
