# L'étape 2 : les correctifs qui ne demandent aucun choix

**Le 25 octobre 2026, la demande.** Le propriétaire, le diagnostic lu :
« Effectue les correctifs simples qui n'ont pas besoin de mes choix. » Ce sont
ceux que le diagnostic rangeait hors de l'architecture. Chacun commence par son
test, vu rouge pour la raison attendue.

**Ce qui est fait.**

- *L'ordre des titres* (`heading-order`). `test_aucun_titre_ne_saute_un_niveau`
  (`tests/test_web.py`) lit, comme axe, ce que la page montre à l'ouverture :
  rouge sur les cinq pages que Lighthouse signalait. Les cartes clés
  (`g.cle`), les points de la Méthode (`g.points`) et les panneaux des
  Carrières types passent de `<h3>` à `<h2>` ; la feuille les dessine comme
  avant (`section.cle > :is(h2, h3)`, `.points .point > h2`,
  `.panneaux > .panneau > h2`). Les intertitres d'une carte, restés `<h3>`,
  gardent la règle des cartes. Les 408 propriétés calculées de ces titres, à
  390 et à 1 440 points, ne diffèrent en rien de celles du site en ligne. Le
  plan de page (`SECTION_DU_PLAN`) et le partage (`:scope > h2`, dans
  `index.html`) suivent ; le témoin des pages ne change que de ces balises.
- *Le rôle des figures légendées* (`aria-allowed-role`, l'arbre que Lighthouse
  lit pour les agents). D'après axe-core 4.14, une `<figure>` qui a un
  `<figcaption>` pour enfant n'accepte que `doc-example`.
  `test_une_figure_legendee_ne_porte_pas_de_role` lit toute la page, sections
  repliées comprises : rouge sur Coût, Droits non cotisés, et les résultats,
  dont le cumul replié échappait à Lighthouse. Graphiques, frises, cascades et
  schémas de Sankey quittent leur `role="group"` ; leur rôle implicite,
  `figure`, est nommé par leur `aria-label`. Le témoin change de 133 balises,
  et de rien d'autre.
- *Le contraste* (`color-contrast`). Le pilote du navigateur
  (`tests/js/ecrans.mjs`) mesure chaque texte sur son premier fond opaque, et
  `test_tout_texte_se_detache_de_son_fond` (`tests/test_ecrans.py`) le juge :
  sur les dix routes, à cinq largeurs, dépliants fermés et ouverts, il ne
  trouve que ce qu'axe avait trouvé, « il manque … € par mois » des cartes de
  résultats, 3,75 pour 4,5. Il s'écrit en `--manque-texte` (#ed9a99), le même
  rouge plus clair : 4,64 sur la carte, 5,56 sur la page ; les aplats des
  graphiques gardent `--manque`.
- *Les décalages du chargement* (CLS). Le pilote ouvre chaque route à neuf, à
  390 et à 1 440 points, et note ses décalages ;
  `test_aucune_page_ne_se_decale_en_se_chargeant` en tient le CLS sous 0,01.
  Rouge au bureau sur les dix routes, 0,889 : « main#contenu de 0 à 112,
  footer de 233 à 0 ». L'en-tête, vide sous l'écran d'attente, poussait
  `<main>` en se remplissant. Le pied, posé sous l'attente, sortait de l'écran
  quand la page arrivait : c'est lui qui portait le décalage près de 1.
  S'y ajoutaient 0,072 à Carrières types et 0,017 à la Méthode : le serif,
  demandé au rendu seulement, arrivait après coup, et le chapeau perdait une
  ligne. L'en-tête est désormais posé plein dès la coquille
  (`gabarit.entete(adresse().chemin)`), le pied au premier rendu
  (`poserLePied`), et les deux polices latines sont préchargées. CLS nul sur
  les vingt chargements.

**Ce que Lighthouse en dit.** Sur un même banc, le site servi d'ici en HTTPS
et HTTP/2, compressé comme GitHub Pages ; avant, l'arbre de 8ae7393 :

| Les dix routes | Perf. mobile | Perf. bureau | Accessibilité | Agentic | B. P., SEO |
|---|---|---|---|---|---|
| avant | 35–59 | 62–64 | 97–100 | 1–100 | 100 |
| après | 58–60 | 87–88 | 100 | 100 | 100 |

Le FCP et le LCP ne bougent pas : 6,3 à 7,0 s et 10,4 à 10,7 s en mobile,
1,3 s et 1,9 à 2,0 s au bureau sur ce banc. Ils attendent le moteur, et ne
descendront qu'avec le pré-rendu (étape 4). Au bureau reste un CLS de 0,005 :
la barre de défilement qui naît quand la page s'allonge décale `<main>` de
quelques points, sans effet sur la note.

**Ce qui reste, sans choix du propriétaire.** Dans les sections repliées, sous
« Pour aller plus loin », un `<h2>` est suivi de `<h4>` (Coût, Droits non
cotisés, Méthode, résultats). Lighthouse ne les voit pas, puisqu'il ne lit que
ce que la page montre, mais une synthèse vocale qui ouvre la section y
tombe. Relever ces `<h4>` en `<h3>` demande à la feuille de leur garder leur
taille, plus petite que celle des `<h3>` d'autres sections repliées.

**Fichiers.** `index.html`, `moteur/style.css`, `moteur/js/gabarit.js`,
`moteur/js/pages.js`, `tests/js/ecrans.mjs`, `tests/test_ecrans.py`,
`tests/test_web.py`, `tests/test_web_revues.py`, le témoin des pages, cette
note et l'action 174. Ni journal de veille : le scénario 1 n'est pas touché.
