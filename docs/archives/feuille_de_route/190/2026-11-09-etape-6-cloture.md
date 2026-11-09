# Étape 6 : la clôture

**Le 9 novembre 2026, ce qui est fait.** Les étapes 2 à 5, menées en
parallèle par quatre sessions dans quatre zones sans fichier commun, sont
toutes sur `main`, et la suite complète est verte sur leur dernier commit
(ad2d8b6, vu par 6b80ae2). L'action passe telle quelle à la fin de
`docs/archives/feuille_de_route.md`, à l'état `fait`, et ce dossier sous
`docs/archives/feuille_de_route/190/`. Aucun code ne change à la clôture.

## Ce que l'action a fait

1. **L'inventaire** (0d03aaf) : vingt et une machines à états implicites
   dans le site, le modèle et l'outillage, presque toutes saines ; deux
   défauts reproduits, un troisième relevé à la lecture du code, une liste
   d'états ouverte, chacun confié à une étape.
2. **Le rendu des pages** (b9d2d38 ; la note de l'étape cite 195b1b6, son
   empreinte avant que l'envoi ne le rebase) : le double message d'erreur
   de deux rendus qui se chevauchent, et un cas voisin, deux échecs
   successifs sur une page recalculée sur place, corrigés ; le relevé
   déposé, reproduit et corrigé pour deux fichiers, non reproduit pour un
   rendu pendant la lecture. Puis l'état du rendu en une seule variable,
   `rendu`, que seule `passer` change ; les courses se jouent dans Chromium
   (`tests/js/ecrans.mjs`, plan `courses`).
3. **Le pont relancé** (778da90) : node mort, le pont se relance à la
   demande suivante, au lieu d'échouer jusqu'à un `pont.fermer()` ; la
   demande en vol échoue encore, avec le journal de node.
4. **Les états des actions** (1332b20) : déclarés une fois, dans
   `scripts/reprise.py`, lus par le tableau de bord, la conservation et
   `tests/test_prose.py` ; tout autre état se refuse, dans la feuille de
   route comme dans l'archive. `pousser.sh` n'est pas touché.
5. **Les récupérateurs** (9030dfd) : vingt-trois machines relevées dans
   `scripts/fetch/`, sans rien télécharger ; deux défauts reproduits et
   corrigés — l'index de la DILA qui se disait construit sur un dump
   tronqué, le cache des rapports à la CCSS qui servait le printemps quand
   l'automne avait paru —, le reste déclaré.

## Ce qui reste, hors de l'action

Rien n'y est un défaut prouvé : chaque point est soit déclaré sans défaut
qui se prouve sans réseau, soit relevé à la lecture et non reproduit.

- *Déclaré par l'étape 5*, dans
  `190/2026-11-09-etape-5-recuperateurs.md` :
  - une réponse coupée, `http.client.IncompleteRead`, qu'aucune boucle
    d'essais ne redemande, au COR, à la Cnav, à Epicycle et au CISIRH : la
    première coupure arrête le récupérateur, sans valeur fausse (82-87) ;
  - la pagination de Melodi, qui s'arrête en silence à la cinquantième page
    pleine et écrit un JSON tronqué ; aucun jeu lu n'en approche (72-74) ;
  - `publier` (`dila_index.py`), qui laisse `<base>.sqlite.gz` dans le
    cache, que `recuperer` prendrait ensuite pour l'index publié : un poste
    qui publie puis récupère se ferait reculer (42-46) ;
  - l'écriture non atomique du cache des rapports à la CCSS : un PDF coupé
    à l'écriture se relirait tel quel (102-105) ;
  - deux lecteurs : la section de la CNAV dans un rapport à la CCSS, qu'un
    saut de page répétant l'en-tête couperait, et qu'aucun test ne couvre
    (121-127) ; le minimum vieillesse de la DREES, dont le régime courant ne
    se remet jamais à nul, de sorte qu'un régime inconnu de la table
    laisserait ses lignes écraser celles du précédent (128-134).
- *Relevé par l'étape 2, non reproduit*, dans
  `190/2026-11-09-etape-2-rendu.md` : après un calcul en échec,
  `rendu.prerendu` garde la route d'une page qui n'est plus toute faite, et
  le rendu suivant de cette route se fait sur place, le message estompé, au
  lieu de l'écran d'attente.
- *Relevé par l'étape 3, sans défaut observé*, dans
  `190/2026-11-09-etape-3-le-pont-relance.md` : chaque `_PontOuvert`
  s'inscrit à `atexit`, qui le garde jusqu'à la sortie du processus, avec
  son tuyau et son journal ; un pont relancé souvent les accumulerait.
- *La limite de l'étape 4*, dans
  `190/2026-11-09-etape-4-etats-des-actions.md` : `pousser.sh` ne joue le
  test des états que si un commit touche la feuille de route ou ses notes ;
  un état mal écrit dans la seule archive passe l'envoi, et la suite de
  GitHub le refuse après.
- *Ce que l'inventaire n'a pas retenu*, et pourquoi : la partie « Ce qui
  n'est pas retenu, et pourquoi » de `190/2026-11-09-etape-1-inventaire.md`
  — les polices, la forme du formulaire, les phases de l'échéancier, à
  revoir au retrait du jumeau, les remplacements du journal, qui
  demanderaient une décision écrite, une marque de l'installation, dans une
  garde.

## Les deux questions au propriétaire

Posées à la clôture, le 9 novembre 2026, sans réponse ce jour-là ; rien
n'est fait de ce qu'elles demandent.

1. Ajouter l'archive aux chemins que `pousser.sh` surveille, pour que la
   limite de l'étape 4 se refuse à l'envoi. `pousser.sh` est une garde : son
   accord d'abord, et le commit porte une ligne `Garde-modifiée: <raison>`
   (action 163).
2. Ce qui reste, ci-dessus : en ouvrir une action `à faire`, ou le laisser
   déclaré ici.
