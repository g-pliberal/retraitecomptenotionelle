# Étape 1 : l'inventaire des machines à états implicites

**Le 9 novembre 2026, ce qui est fait.** Le dépôt est relu pour ce qui garde
un état sans le nommer : les variables de module (seuls `routeur.js`,
`gabarit.js` et le compteur d'appels de `droit/liquidation.js` en ont), les
marques posées sur le document (`dataset`, classes, `aria-*`, `hidden`,
`disabled`), les champs nuls qu'une méthode remplit pour une autre, les
mémoires (`localStorage`, fichiers sous `.cache/`), les processus gardés
ouverts. Vingt et une machines, presque toutes saines. Deux défauts sont
reproduits, un troisième relevé à la lecture du code, et une liste d'états
reste ouverte : chacun va à une étape. Les cent cinquante-trois
récupérateurs de `scripts/fetch/` n'ont pas été lus un à un : c'est
l'étape 5. Les numéros de ligne sont ceux du commit 810797d.

Chaque étape ne lit ici que sa partie : le site, l'étape 2 ; le pont,
l'étape 3 ; les états des actions, l'étape 4 ; les récupérateurs, l'étape 5.
Le reste est sain, ou n'est pas retenu, et dit pourquoi.

## Le site : l'étape 2

L'étape 2 ne touche que `moteur/js/routeur.js` : les machines 1 et 6 y
portent les défauts ; les autres sont saines.

1. **Le rendu d'une page** — `routeur.js:283-499`, `3172-3217`. Son état
   est réparti entre `body[data-pret]` (prête), `body.calcul-en-cours` et
   `#contenu[aria-busy]` (occupée), `#contenu[data-prerendu]` (la page toute
   faite, ôtée au premier recalcul et jamais remise), `routeAffichee` (nulle
   quand rien n'est affiché ou que le dernier rendu a échoué),
   `requeteAffichee`, `ecranRendu` et `demiRendue`, et `numeroDeRendu`, qui
   fait gagner le dernier rendu. En fait : la page toute faite, animée
   (`hydrater`) ou occupée — estompée sur place, ou sous l'écran
   d'attente —, puis le moteur qui se charge, puis la page rendue, le calcul
   en échec ou le chargement en échec. Déclencheurs : le démarrage,
   `hashchange`, `resize` après 250 ms (325-349).
   *Défaut, reproduit.* Deux rendus qui se chevauchent quand le moteur ne se
   charge pas posent deux messages d'erreur. Dans Chromium, sur
   `simuler/#naissance=1980`, le paquet de données refusé au bout de 1,5 s
   (`page.route`) et l'adresse changée à 0,5 s, la page porte deux
   `#contenu > .erreur` ; un rendu seul en porte un. La cause :
   `echecDuChargement` (95-108) passe avant la garde
   `numero !== numeroDeRendu` (373-379, 425-431) ; le premier `echec()`
   remplace l'écran d'attente, le second, qui ne le trouve plus, se place
   devant le premier.
2. **Les chargements à la demande** — `routeur.js:45-60` (`modules`),
   `123-130` (`preparation`), `2312-2323` (`policesDemandees`). Une promesse
   gardée : rien, en cours, prêt. Les deux premières reviennent à rien sur
   un échec, et le calcul suivant réessaie ; celle des polices avale l'échec
   et ne réessaie jamais.
3. **La saisie retenue** — `routeur.js:964-1298`, `1702`. La clé
   `retraite-notionnelle.simulateur` tient `requete` et `brouillon` : vide,
   l'une, l'autre, les deux. Calculer retient la simulation et efface le
   brouillon ; taper écrit le brouillon, ou l'efface quand le formulaire
   redevient ce que le rendu a écrit (`formulaire._rendue`) ;
   « Réinitialiser » vide tout ; reprendre sous d'autres règles récrit la
   requête et efface le brouillon ; une autre version, ou une valeur abîmée,
   se lit vide. `reglesVues` (303, 457, 1092), propre à la visite, change le
   sens d'une adresse sans règles.
4. **Le dernier geste** — `routeur.js:706-714`, `352-360`, `882-958`.
   `declencheur`, une case à usage unique qui vaut deux secondes : `calcul`,
   `navigation` ou `sur-place`, avec `effacement` et `retrait`. Il dit où
   vont le focus et le défilement, et si la saisie est retenue.
   `premierRendu` (286) en est un second, à usage unique.
5. **La forme du formulaire, dans l'adresse** — `saisie.js:199-295`,
   `942-1006` ; `pages.js:2108-2138`. `situation` (actif, retraite) donne le
   défaut de `saisie_par` (revenu, pension) ; `montants` (net, brut) ;
   `unite_revenu` (euros, ou multiple du salaire moyen), une adresse sans
   unité se lisant au multiple (951). Les bascules sont les transitions, et
   `requeteBasculee` traduit les montants de chacune. Chaque bascule
   retourne une clé, dans un ordre que rien ne déclare — net ou brut, puis
   l'unité, puis la situation — : un lien qui en changerait deux n'en
   ferait qu'une. Aucun défaut constaté.
6. **Le relevé déposé** — `routeur.js:1453-1656`. Rien, en lecture,
   rempli, ou l'un de quatre refus — un PDF sans texte, aucune année
   reconnue, trop d'années, une erreur de lecture ; l'état n'est que la
   classe et le texte du compte rendu.
   *Défaut, relevé à la lecture du code, non reproduit.* Aucune garde.
   `rapport`, `champ` et `formulaire` sont pris au début (1543-1545), puis
   viennent cinq attentes : les octets, deux imports, la lecture du PDF, le
   moteur, qui prend plusieurs secondes au premier calcul. Un second fichier
   déposé entre-temps lance une seconde lecture, et la plus lente écrit la
   dernière ; un rendu entre-temps remplace le contenu de `#contenu`, et la
   lecture écrit dans des nœuds que la page a retirés : le lecteur ne voit
   rien.
7. **Les boutons de partage** — `routeur.js:2945-3028`. « Partager » :
   actif, la composition (désactivé), puis partagé, abandonné, image
   enregistrée et message copié, image enregistrée et message à copier à la
   main, ou l'échec, et actif de nouveau. « Publier sur X » : la fenêtre
   d'abord, puis l'image, enregistrée ou non.
8. **La lecture d'un graphique** — `routeur.js:2006-2150`, et la cascade
   jusqu'à 2280. `_rang` de chaque figure, nul ou une année, que le pointeur
   et le clavier mènent tous deux : le survol le pose ; la sortie de la
   figure, `focusout` et Échap l'effacent ; les flèches, Début et Fin le
   déplacent, depuis la dernière année s'il est nul.
9. **Les petites bascules** — `routeur.js:1709-1779`, `283`, `389`, `463` :
   les menus du téléphone (`aria-expanded`), les bulles du glossaire, une
   seule ouverte à la fois, Échap rendant le focus, et les options qui
   restent dépliées d'un rendu à l'autre.
10. **Le contexte de rendu du gabarit** — `gabarit.js:172-257`, `1430`,
    `1775`, `2518-2583`. `OPTIONS`, `PAGE`, `ECRAN` et `DEMI_COLONNE`,
    posés par `pages.rendre` avant chaque rendu : un état de module voulu,
    et dit. `CADRE` et `GEOMETRIE_SANKEY`, posés au début de chaque dessin
    et lus par ses aides : l'ordre fait la justesse. Hors de l'étape 2, qui
    ne touche pas au gabarit.

## Le pont : l'étape 3

15. **Le pont** — `src/retraite_notionnelle/pont.py:146-283`. `_OUVERT` :
    fermé, ouvert sur la signature du paquet — sa date, sa taille, la garde
    des présomptions —, relancé quand elle change, fermé par `fermer()` ou à
    la sortie du processus. `_JUMEAU` (186-232) compte les contextes
    imbriqués : le portage, ou le jumeau Python.
    *Défaut, reproduit.* Node mort, le pont ne se relance pas : `_ouvert()`
    (266-273) ne rouvre que sur une signature changée. Node tué
    (`pont._OUVERT._processus.kill()`), la deuxième demande de
    `pont.droit` lève « pont.mjs : node s'est arrêté », la troisième aussi,
    et seul `pont.fermer()`, que seuls les tests appellent, rend la
    quatrième juste. Fermer un pont mort ne ferme pas non plus son tuyau
    d'entrée, qui garde la demande non écrite : Python le signale en le
    ramassant (`Exception ignored … BrokenPipeError`).

## Les états des actions : l'étape 4

21. **Les actions de la feuille de route** : `à faire`, puis `en cours`,
    puis `fait`, `abandonnée` ou `archivée`, l'action passant alors à
    l'archive. L'état est le mot entre accents graves du titre, que
    `reprise.TITRE_D_ACTION` lit.
    *Défaut.* La liste n'est fermée nulle part. Les états clos s'écrivent
    trois fois (`tests/test_prose.py:1024`, `:1101`,
    `scripts/conservation.py:248`) ; « en cours » se compare en toutes
    lettres trois fois (`scripts/reprise.py:117`,
    `scripts/tableau_de_bord.py:345`, `tests/test_prose.py:1056`). Un état
    mal écrit, `en-cours`, ferait une action ni close ni en cours : rangée
    parmi les ouvertes, que `reprise.py` n'imprime pas, que le test des blocs
    « Reprise » ne regarde pas et que le tableau de bord ne compte pas.
    Avant celle-ci, la feuille de route portait 26 actions en cours et 21 à
    faire ; l'archive, 139 faites, 2 archivées et 2 abandonnées.

## Les récupérateurs : l'étape 5

Non inventoriés. Ce qu'on y cherche : un lecteur qui tient la section, le
tableau ou le régime courant d'un document, et qui les remet à zéro, ou
non, sur un en-tête (comme le relevé lu, machine 14) ; un téléchargement qui
reprend, s'arrête ou réessaie ; une mémoire, sous `.cache/` ou ailleurs, qui
se périme. Par `Grep` d'abord, ou par l'éclaireur, puis la seule fenêtre
utile ; une session qui s'arrête en cours d'étape dit dans son bloc
jusqu'où elle a lu.

## Le reste de l'inventaire, sans défaut

11. **La vie d'une pension** — `moteur/js/echeancier.js:126-205`,
    `533-663`, et son jumeau `echeancier.py`. La machine du domaine.
    `parcourir` enchaîne, dans cet ordre, la radiation à la limite d'âge, la
    retraite progressive, le ou les départs, la réversion (au décès déclaré,
    ou d'essai), l'échéance, le cumul emploi-retraite, la seconde pension et
    les régimes que l'activité après le départ ouvre. L'état tient dans des
    champs nuls (`progressive`, `provisoire`, `plancher`, `auDepart`,
    `aujourdhui`, `reversion`, `dureesAuDepart`) et dans la table
    `progressives` ; les phases suivantes complètent `auDepart` et lisent ce
    que les précédentes y ont écrit : l'ordre fait la justesse. La retraite
    progressive est une machine dans la machine : examinée, close ou
    ouverte, liquidée à titre provisoire, réexaminée avec sa durée, le
    plancher posé, puis remplacée dans sa lignée par la liquidation
    définitive, dont l'événement devient `pension_definitive` (170-176,
    578-587).
12. **Le journal** — `moteur/js/journal.js:95-146`, et `journal.py`.
    Explicite, lui : on y ajoute sans effacer, `remplace` chaîne une
    composante à ses révisions, `servi` garde la dernière de chaque lignée.
    Implicite : quelle sorte d'entrée peut en remplacer quelle autre ;
    `inscrire` ne vérifie que l'existence de l'entrée remplacée. `annule`,
    « l'événement en attente qu'elle annule », est au contrat C.8 et aux
    deux jumeaux, mais rien ne l'écrit : l'événement en attente n'existe
    pas encore.
13. **La lecture d'un PDF** — `moteur/js/lecture-pdf.js:855-939`. Un
    interprète écrit à la main, en variables locales : la matrice du texte,
    le repère de la page, la pile de `q` et `Q`, qui sauve le repère, la
    police et l'interligne, et `dansTableau` dans un tableau `TJ` ; puis les
    morceaux mis en lignes (`assembler`, 976-1015).
14. **La lecture d'un relevé** — `moteur/js/releve-lu.js:578-760`. Ligne à
    ligne, deux registres : `courant`, la dernière base qui porte une
    carrière, et `section`, le dernier régime nommé. Un en-tête de tableau
    remet `section` à nul, pas `courant`. La première naissance et le
    premier NIR l'emportent ; la date de fin la plus tardive aussi.

Dans la fabrique et l'outillage :

16. **La mémoire des calculs** — `src/retraite_notionnelle/memoire.py:444-596`.
    Par clé : absent, puis en calcul sous un verrou du système — les autres
    attendent trente minutes au plus, puis calculent pour eux —, puis gardé
    (pickle, remplacement atomique), relu une fois le verrou pris. Deux
    compteurs par-dessus : `modele_modifie`, et `lecture_seule`, propre à
    chaque fil.
17. **L'envoi** — `scripts/pousser.sh:79-153`. HEAD contient
    `origin/main`, le suit ou en diverge ; puis l'avance rapide, ou le
    rebasage, dont l'état est le dossier `rebase-merge` de git : la version
    de `main` gardée pour un fichier marqué `-merge`, un commit vidé sauté,
    cent tours au plus, puis l'abandon.
18. **Le test d'abord** — `.claude/hooks/tdd.py:157-203`. Deux marques,
    `.cache/tdd/rouge` et `.cache/tdd/rappel`, par session et par commit ;
    tout commit neuf, amendé ou rebasé compris, les remet à zéro.
19. **Le verdict de la suite** — `.github/etat_suite.yaml`, que lit
    `.claude/hooks/etat-suite.sh` : la suite verte ou rouge, la garde des
    présomptions, et le nombre de commits depuis.
20. **L'installation d'une session** — `.claude/hooks/session-start.sh`.
    L'installation en arrière-plan ne laisse ni marque de fin ni marque
    d'échec : « encore en cours » et « échouée » se ressemblent.

Ressemblent à des machines à états, et n'en sont pas : les statuts du cumul
emploi-retraite (`droit/cumul.js:31-48`), une liste fermée qu'une table de
décision choisit mois par mois, avec une seule mémoire par année ; le pli
des tableaux (`routeur.js:1828-1890`), recalculé de la largeur à chaque
fois ; le pilote (`pilote.js`), un point fixe ; `liquidation.Etat`, une
valeur qui ne change pas.

## Ce qui n'est pas retenu, et pourquoi

- *Les polices qui ne se rechargent pas* (2) : le repli sur les polices du
  système est écrit dans la déclaration ; voulu, semble-t-il.
- *La forme du formulaire* (5) : un lien, une clé ; aucun défaut constaté.
- *Les phases de l'échéancier* (11) : aucun défaut. Les rendre explicites
  toucherait les deux jumeaux, au rang 42 du retrait
  (`python scripts/jumeaux.py echeancier`), et les trente fiches qui citent
  `echeancier.py` : à revoir au retrait du jumeau.
- *Les remplacements du journal, et `annule`* (12) : l'entrée du journal et
  la règle « le journal est l'état » sont au noyau (`docs/architecture.md`,
  § 13.1) ; borner `remplace` en changerait le sens, ce qui demande une
  décision écrite.
- *Une marque de l'installation* (20) : `session-start.sh` est une garde,
  qui ne se touche qu'avec l'accord du propriétaire, demandé avant
  (action 163).
