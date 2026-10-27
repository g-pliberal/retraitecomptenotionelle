# Le style de chaque page, dans son HTML

**Le 27 octobre 2026, la demande.** Le propriétaire, devant la proposition du
premier affichage en mobile (`2026-10-27-proposition-premier-affichage.md`) :
« On fait la proposition 1 pour l'instant. » La proposition 2, alléger Coût et
Droits non cotisés de leurs tableaux de données, attend.

## Ce qui est fait

- **`scripts/feuille_de_page.py`** choisit, pour une page, les règles de
  `moteur/style.css` qui peuvent la toucher : une règle est gardée quand l'un de
  ses sélecteurs ne demande que des classes, des identifiants, des balises et des
  attributs présents dans la page, ou posés par le routeur — les mots de ses
  chaînes, et les attributs qu'il pose par `dataset`. Les pseudo-classes et les
  sélecteurs fonctionnels ne demandent rien ; `@media`, `@supports` et
  `@container` gardent leur condition ; l'impression reste à la feuille entière ;
  les polices sont toujours déclarées, une animation quand une règle gardée la
  nomme. En Python, sans dépendance ni navigateur à la fabrique.
- **Chaque page porte ce style en tête** (`moteur/page.html`, écrit par
  `construire_pages.py`), adresses relatives à la page, et charge la feuille
  entière sans bloquer : déclarée pour l'impression, rendue effective par son
  `onload`, ou par le routeur sous une politique de sécurité qui refuserait les
  gestionnaires en ligne ; sans script, par le lien du `<noscript>`.
- **Les tests** : `tests/test_style_de_page.py` (douze cas de choix des
  règles) ; `test_pages_en_dossier.py` (chaque page porte son style, plus petit
  que la moitié de la feuille, sans l'impression, et la feuille entière en
  différé) ; dans Chromium, `test_ecrans.py` ouvre chaque page deux fois, avec la
  feuille entière puis sans elle, à 390 et 1 440 points, et compare chaque
  élément — sa boîte, sa couleur, sa police — ; une page sans son `onload` doit
  quand même rendre la feuille effective.

## Ce que le chemin a appris

- **Le premier essai manquait les tableaux repliés en mobile.** Le routeur
  replie un tableau trop large en lui posant `data-pli` par `table.dataset.pli` :
  le nom de l'attribut n'est écrit nulle part en toutes lettres, et les règles du
  repli manquaient au style de quatre pages, à 390 points. La comparaison dans
  Chromium l'a montré ; les attributs posés par `dataset` comptent désormais.
- **Un échec du test des décalages, une seule fois.** La première suite
  complète, jouée à pleine charge, a vu `test_aucune_page_ne_se_decale_en_se_chargeant`
  échouer, sans que le détail en soit gardé ; ni la seconde suite complète, ni
  six passages du test sous charge ou processeur saturé ne l'ont reproduit. La
  seule cause qui produise un décalage au chargement est l'arrivée des polices
  après la première peinture : à retard égal (0,6 s), elle décale autant avant ce
  changement qu'après, et jusqu'à 0,28 sur Méthode à 390 points, où le bandeau
  change de hauteur quand la police arrive. Un routeur retardé d'une seconde ne
  décale rien, ni un réseau mobile lent émulé (1,6 Mb/s, 150 ms, processeur
  ralenti quatre fois), où le premier contenu passe de 1,9 s à 0,6 s. Les polices
  sont désormais demandées avant le style de la page. Le bandeau qui change de
  hauteur avec la police reste une fragilité ancienne, à traiter à part : des
  polices de repli à leurs métriques (`size-adjust`).
- **Le style choisi pèse un peu plus que la mesure** : de 7 à 9 Ko compressés
  par page au lieu de 4 à 7, parce qu'il garde aussi ce que le routeur pourrait
  poser. C'est le prix d'un choix sans navigateur, et d'aucune règle manquante.

## Les mesures, en local, le 27 octobre 2026

Lighthouse 13, mobile, trois mesures par page, avant (l'étape 5) et après ;
médianes du premier contenu et du plus grand, en secondes.

| Page | Avant | Après |
|---|---|---|
| Programme | 99, 99, 99 — 1,58 / 1,96 | 100, 100, 100 — 1,11 / 1,71 |
| Pourquoi changer | 98, 99, 98 — 1,66 / 2,11 | 100, 100, 100 — 1,11 / 1,72 |
| Méthode et sources | 95, 98, 96 — 1,86 / 2,46 | 97, 99, 99 — 1,26 / 1,86 |
| Coût | 97, 94, 97 — 1,87 / 2,32 | 99, 99, 99 — 1,43 / 2,03 |
| Simuler | 97, 99, 99 — 1,55 / 2,08 | 99, 98, 99 — 1,25 / 2,01 |
| Droits non cotisés | 99, 99, 99 — 1,55 / 2,00 | 97, 99, 99 — 1,42 / 2,02 |
| Carrières types | 98, 100, 98 — 1,55 / 2,16 | 100, 100, 100 — 1,10 / 1,70 |

Le CLS reste nul, les quatre autres catégories à 100.

**En ligne**, le 27 octobre 2026, la suite verte et la copie déployée, deux
mesures (la première a vu GitHub Pages répondre 503 sur `config.js` pendant les
résultats : le simulateur a dit qu'il ne pouvait se charger, et cette mesure-là
ne compte pas pour eux). Performance mobile, de l'étape 5 à celle-ci :
Programme 95 → 99 et 99, Simuler 99 → 99 et 98, Coût 98 → 97 et 97, Pourquoi
changer 98 → 99 et 99, Partager 100 → 99 et 99, Le saviez-vous ? 99 → 100 et 99,
Carrières types 99 → 98 et 99, Droits non cotisés 99 → 98 et 98, Méthode 98 → 99
et 99 ; au bureau, 100 partout. Le premier contenu en mobile tombe à 1,2 à 1,4 s
sur la plupart des pages (Coût et Droits non cotisés, 1,5 à 1,8 s). Deux choses à
suivre :

- **Le saviez-vous ?**, à la seconde mesure, décale de 0,016 en mobile : la
  page peint désormais avant que ses polices soient là, et leur arrivée la
  recompose. C'est la fragilité notée plus haut, plus exposée qu'avant.
- **Les résultats** : 70 au lieu de 73 en mobile, 80 au lieu de 85 au bureau.
  Le premier contenu venant plus tôt, la fenêtre du TBT s'ouvre plus tôt, et le
  calcul du moteur y tombe davantage (2,3 s de TBT mobile au lieu de 1,6) : la
  page est plus vite visible, la note ne le dit pas.

## Ce qui reste

- **Les polices sans décalage** : des polices de repli à leurs métriques
  (`size-adjust`, `ascent-override`), ou `font-display: optional`, qui garde la
  police du système le temps d'une première visite lente — un choix sur
  l'identité de l'affiche, au propriétaire.
- **La proposition 2**, au propriétaire : les tableaux de données de Coût et de
  Droits non cotisés chargés à l'ouverture de leur volet, contre leur lecture
  sans script.
- **Le sort des résultats d'une simulation** (décision 3), et l'hôte à sa
  prochaine copie.
