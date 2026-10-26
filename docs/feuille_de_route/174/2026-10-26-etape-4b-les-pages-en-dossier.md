# L'étape 4 (a) et (b) : le routeur sorti d'index.html, une page par dossier

**Le 26 octobre 2026, la demande.** Le propriétaire, après la description de
l'étape 4 : « Vas-y, fait ça ici. » Les deux premiers temps sont faits et
publiés ; le pré-rendu (c) reste. Le détail de ce que la décision engage est
dans `2026-10-26-proposition-des-adresses.md` et dans la note de décision 0004
(`docs/decisions/0004-une-adresse-par-page.md`) ; celle-ci dit ce qui a été
fait, et ce que le chemin a appris.

## Ce qui est fait

- **Le routeur est un module** (`moteur/js/routeur.js`, 015a9b4) : les 2 967
  lignes du script en ligne d'`index.html`, que toutes les pages chargent
  désormais. Ses imports et le paquet de données se résolvent depuis lui,
  non depuis la page ; hors de l'empreinte du modèle (`HORS_DU_MODELE`), le pont
  ne l'important pas.
- **Les adresses ont un module** (`moteur/js/adresses.js`, 42d9269 puis cette
  étape) : `lireAdresse(chemin, ancre)` lit les deux formes — la page dans le
  chemin et le lecteur derrière le `#`, ou l'ancienne, la page derrière le `#` —
  et `ecrireAdresse` écrit la nouvelle forme d'une adresse lue. Les deux pages
  fondues le 23 septembre 2026 y vivent (`ANCIENNES_ROUTES`).
- **Le gabarit sait où va chaque page** : `PAGES`, `dossierDe`, `versLaPage`,
  et `lien`, `lienAvecRequete`, `route` écrivent chaque adresse relative à la
  page rendue (`rendre` la pose, `poserPage`), la section d'abord derrière le
  `#`, les réglages ensuite : `../methode/#sources&indexation=prix`. Chaque
  renvoi vers une section (`data-vers`) nomme aussi la section dans son
  adresse, qui la porte d'une page à l'autre ; `sectionEnAttente` n'existe
  plus.
- **Les huit pages en dossier** (`simuler/`, `cout/`, `risque/`, `partager/`,
  `saviez-vous/`, `cas-types/`, `avantages/`, `methode/`) sont fabriquées par
  `scripts/construire_pages.py` depuis `index.html` — ses chemins remontés d'un
  cran, le titre et la description de la page —, refaites par `regenerer.py`,
  déclarées `-merge`. On retouche `index.html`, jamais une page de dossier.
- **Le routeur redirige les anciennes adresses**, avant même de charger le
  paquet : `location.replace` vers le dossier de la page visée, ou
  `history.replaceState` quand c'est l'accueil. L'adresse est remplacée, non
  empilée. Un lien vers la page où l'on est ne recharge rien ; aller à une autre
  page charge son dossier ; « Calculer » depuis l'accueil retient la saisie
  avant de partir, le document neuf ne sachant pas de quel geste il vient.
- **Les documents** : le document d'intégration dit le changement en tête, le
  même jour (adresses, dossiers à copier, hôte), la carte du dépôt, le README,
  le parcours de présentation, l'annexe C.9 de l'architecture et sa version du
  26 octobre 2026.

## Ce que les tests tiennent

- `tests/test_adresses.py` : lecture, écriture, dossiers et chemins relatifs
  (l'étalon est la résolution d'URL de la bibliothèque standard, de toute page
  à toute page, sous la racine d'un hôte ou un dossier).
- `tests/test_pages_en_dossier.py` : chaque page à jour, son titre, sa
  description, ses chemins un niveau plus haut, chaque ressource qui existe.
- `tests/test_adresses_navigateur.py` : dix-sept scénarios dans Chromium, dont
  chaque ancienne forme d'adresse — arrivée, titre, ce que la page montre,
  section ouverte, une seule entrée d'historique —, les liens du bandeau, un
  renvoi vers la section d'une autre page, « Calculer » depuis l'accueil.
- `tests/test_web*.py` : tout lien interne, résolu depuis sa page, mène à l'une
  des neuf pages, et toute section nommée derrière un `#` existe sur sa cible.
- Le pilote des écrans ouvre chaque route à neuf : `test_ecrans.py` passe de
  25 s à 90 s, cinquante chargements au lieu de cent changements d'ancre.

## Ce que le chemin a appris

- **La suite était rouge sur `main` après l'étape (a)**, quatre tests de
  `test_formulaire.py` et `test_affirmations.py` lisant encore le script
  d'`index.html` : réparée en c7288a3, avant tout. Les tests de la zone et la
  suite rapide ne les jouaient pas. Pour un changement qui déplace du code d'un
  fichier à l'autre, la suite complète se joue ici avant l'envoi
  (6 297 tests, dix-huit minutes) ; celle-ci l'a été avant celui-ci.
- **Une ancre morte** : `g.lien("/methode", "indexation")` visait une section
  qui n'existait pas, et l'argument était ignoré. Le nouveau test (toute
  section nommée existe) l'a trouvée ; le dépliant des règles d'indexation de
  Méthode porte désormais l'identifiant `indexation`.
- **`reglesVues` ne passe plus d'une page à l'autre** : c'est un état du
  routeur, et chaque page est un document. Il ne servait qu'à distinguer, sur le
  simulateur, une adresse sans règles qui est un choix du lecteur d'une absence
  d'avis ; les liens du site portant ses règles, le seul cas perdu est une
  adresse tapée à la main après avoir vu des règles non défaut. Pas de remède
  écrit.
- **`innerText` rend les capitales du style** : le pilote lit `textContent`.

## Ce qui reste

L'étape 4 (c), le pré-rendu : chaque page écrite toute faite par
`construire_pages.py` (en-tête, corps, pied), le moteur sorti de l'en-tête,
l'adresse canonique de la copie du parti. Puis l'étape 5, le moteur à la
demande. Reste au propriétaire le sort des résultats d'une simulation, et
l'hôte à sa prochaine copie (ses deux retouches d'`index.html`, `plf-embedded`
à chaque chargement du cadre).
