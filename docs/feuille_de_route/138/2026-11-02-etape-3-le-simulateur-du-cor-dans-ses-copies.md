# Étape 3, vingt-sixième partie : le simulateur du COR, retrouvé dans ses copies, et le geste de l'âge confronté à son code

**La demande.** Le propriétaire, le 2 novembre 2026 : « À défaut d'avoir un
simulateur du Cor qui fonctionne, ne peut-on pas prendre le simulateur du Cor
dans une archive ? » ; puis, des deux suites proposées, « 2 » : confronter
`releve_age` au code du simulateur, sur ses séries de 2019 et de 2021.

**Ce qui a été trouvé.**

- *Le simulateur, toujours fermé* : sa page n'a pas changé depuis le 29
  juillet 2026 (son `Last-Modified`, relu le 2 novembre).
- *L'archive du web refuse la session* : web.archive.org coupe la connexion,
  archive.org répond 429, de l'Internet Archive elle-même, comme les 13 et
  18 octobre ; arquivo.pt répond 403, la passerelle Memento et Common Crawl
  ne répondent pas.
- *Trois copies sur GitHub*, que le registre citait comme des « reprises »,
  clonées par git (l'HTML de GitHub est refusé, ses fichiers bruts servis) :
  - `nosretraites/roc-retraites` (commit `d375f10`, 28 janvier 2020) garde
    le site entier — la page « Simulateur - Conseil d'orientation des
    retraites », son code AngularJS (`js/script.js`), ses données
    (`fileProjection.json`), sa documentation technique, sa FAQ —, « revu »
    par le collectif Nos retraites, qui y a ajouté le rapport de la pension
    nette au salaire net et des graphiques ;
  - ses données et sa documentation sont identiques à l'octet à celles de
    `brunoscherrer/retraites` (`f3c2d92`), que le dépôt lisait déjà : le
    millésime de juin 2019, aux six scénarios de son code (des salaires à
    +1,8, 1,5, 1,3 et 1 % sous un chômage de 7 %, +1,8 % sous 4,5 %, +1 %
    sous 10 %) ;
  - `ChallengesRedac/simulateurRetraite` (`3130716`, 9 janvier 2023) garde
    un autre millésime du même fichier, qu'il nomme aussi
    `donneesCor2021.json` : toutes ses séries y changent — en 2070, au
    scénario 1, 22,95 millions de retraités au lieu de 24,33.
- *Les conditions du COR* : ses mentions légales soumettent la reproduction
  de ses documents, hors notes de séance, « à l'accord de leur auteur ou
  éditeur ». Les fichiers restent dans `data/brut/` ; le témoin ne garde que
  les séries du test.

**Le code du simulateur.** Il ne cherche pas l'âge : on règle l'âge, le taux
et la pension, et il dit le solde, `B·(T − nb·(P + dP))`, où
`nb = (NR − G·Δ) / (NC + 0,5·G·Δ)` compte les retraités par cotisant après
un recul Δ (l. 403 et 411). Chaque année de recul retire G retraités, G
l'« effectif moyen d'une génération arrivant aux âges de la retraite », et en
ajoute la moitié aux cotisants : le geste de `releve_age`, sur une pyramide
où chaque âge compte G personnes.

**Ce qui est fait.**

- *Un blocage de plus au manifeste*, `retire` (`source_locale.BLOCAGES`,
  en-tête de `data/sources.yaml`) : le producteur ne sert plus le document,
  seules des copies le gardent ; le miroir désigne celle qu'on lit,
  l'empreinte la contrôle. `--recuperer` les dépose dans `data/brut/`,
  `--publier` les laisse.
- *Deux jeux*, `cor_simulateur_2019` et `cor_simulateur_2021`, sur l'adresse
  du fichier, chacun avec sa copie, son empreinte, son nom local et sa
  rediffusion `interdite`.
- *Le récupérateur* `scripts/fetch/cor_simulateur.py`, par
  `lire_ou_telecharger`, et *le témoin* `tests/temoins/cor_simulateur.json` :
  NR, NC, G, T, P, dP, PdP et A, aux six scénarios, de 2030 à 2070 de cinq en
  cinq.
- *Les tests.* `tests/test_leviers.py` tient le témoin et confronte le geste
  de l'âge au code du simulateur, à chaque millésime, scénario et année :
  sur ces 108 cas, le recul de `releve_age` est la racine de l'équation du
  simulateur à un cent-millième d'année près, et avance l'âge quand le
  système a une marge. `tests/test_source_locale.py` tient les deux jeux
  retirés, et range le récupérateur parmi ceux qui lisent un document.
- *Le registre* (`simulateur_cor` : sa licence, sa confrontation, son bilan,
  sa copie) et la ligne `cor_simulateur` des sources à explorer, qui reste
  `a_explorer` pour sa version rouverte.

**Ce que la confrontation montre.**

- *Le geste est le même.* Sur les séries du simulateur, `releve_age` rend le
  recul qui annule son solde, de −4,7 ans (2021, scénario 5, en 2070) à +2,5
  (2019, scénario 6, en 2070). La part des retenus comptés parmi les
  cotisants que le dépôt garde, la moitié, est celle de son code.
- *Ce qu'il ne dit pas : la part du rapport de 2026.* Pour que le geste
  refasse les âges d'équilibre de la figure 2.24, il en faut les deux tiers
  (troisième partie). Les séries du simulateur écartent deux explications.
  Son G est la population de l'INSEE que le dépôt déplace, à 2 % près : 855
  milliers en 2030 contre 872, 871 en 2070 contre 856. Ses retraités, de 0,4
  à 0,5 million plus nombreux que ceux du dépôt en 2030 (18,66 et 18,57
  millions contre 18,20), porteraient la part qui refait les âges de 2026
  plus haut encore : de 0,67 à 0,88 selon l'année, le millésime et le
  scénario, au lieu de 0,62 à 0,73. Ces comparaisons croisent deux
  millésimes : elles orientent, sans trancher.

**Ce que ça déplace.** Rien : aucun chiffre de page, aucun témoin du site ;
un témoin de plus, que rien ne lit hors des tests.

**Ce qui reste**, de cette partie ; le reste de l'étape 3 est dans la note de
la première.

1. *Le dernier millésime du simulateur*, celui qu'il servait avant sa
   fermeture, à rapporter d'un poste : l'archive du web en liste les
   versions (`https://web.archive.org/cdx/search/cdx?url=cor-retraites.fr/simulateur/fileProjection.json&collapse=digest`)
   et sert chacune
   (`https://web.archive.org/web/<horodatage>id_/https://www.cor-retraites.fr/simulateur/fileProjection.json`).
   Déposé dans `data/brut/`, il prendrait un jeu de plus au manifeste ; ses
   retraités, plus proches du rapport de 2026, diraient mieux quelle part le
   COR retient.
2. *La date du millésime de Challenges*, que seul son nom dit ; l'archive du
   web la donnerait aussi.
3. *La version rouverte*, aux scénarios révisés.
