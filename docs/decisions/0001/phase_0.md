# Phase 0 de l'architecture — la passation

*Écrit le 25 septembre 2026 par la session qui a conçu et éprouvé
l'architecture, pour la session qui lance la phase 0. À lire en premier.*

## Ce qui est décidé, et ne se rediscute pas

L'architecture est `docs/decisions/0001-architecture.md`, version 5.4, décidée
par le propriétaire le 25 septembre 2026. Trois séries de vérifications et une
contre-épreuve l'ont éprouvée ; son § 14 les raconte. Elle est **gelée** : on
ne la modifie pas. Ce qui devrait y changer passe par une note de décision
(son § 13.3).

Le propriétaire a pris lui-même ces décisions ; elles s'imposent :

- **Principe 3 élargi.** OpenFisca n'est qu'un modèle public parmi d'autres,
  et aucun ne fait autorité sur la loi (§ 3.1 et 3.4).
- **Toutes les sources sont gardées**, Catala, PENSIPP et LexImpact compris,
  pour ce qu'elles valent. Leurs licences, et ce qu'elles permettent : § 3.4.
- **Simulateurs officiels : les quatre voies du § 3.5**, et jamais de
  sollicitation des caisses, ni demande d'exemples, ni demande d'accord, ni
  demande de documents.
- **Trois règles de conduite** (L'essentiel) : restructurer ne change aucun
  résultat ; rien ne se perd ; ce qu'on apprend n'est jamais bloqué (§ 9.2).
- **La preuve** (§ 3.2) et la façon de trancher une divergence (§ 3.3) : rien
  sans source vérifiable, jamais de choix en silence.
- **Le tableau de bord** (§ 9.1), dès la phase 0.

## Ce que fait la phase 0

Aucun résultat ne change (§ 11 et 12). Un commit par étape, dans cet ordre :

1. **`docs/architecture.md`**, l'état de l'architecture, tiré de la note
   0001 : L'essentiel, les § 2 à 13, les annexes A, B et C. Les § 1 et 14 sont
   des récits : ils restent dans la note, qui ne bouge pas.
   - Le déclarer dans `data/reference/prose/zones.yaml`, section par section.
     Une section d'état n'admet aucun chiffre nu (`docs/fraicheur.md`).
   - La note 0001 donne beaucoup de chiffres datés : 3 millisecondes, 91
     régimes… Dans `docs/architecture.md`, chacun devient soit une ancre sur
     une sonde, soit un renvoi au tableau de bord ou à la note. C'est la règle
     du § 9.3 : les chiffres qui décrivent le dépôt sortent de la prose.
   - Puis lancer `python scripts/verifier_prose.py --corriger`, et
     `python -m pytest tests/test_prose.py`.
2. **Le tableau de bord.** `scripts/tableau_de_bord.py` écrit `docs/etat.md`.
   Il part de la maquette `docs/decisions/0001/tableau_de_bord.py`, qui lit
   les registres d'aujourd'hui.
   - Le déclarer `produit` dans `zones.yaml`, avec un test qui refuse une copie
     périmée, comme `test_les_tableaux_produits_ne_sont_pas_perimes`.
   - **Piège** : la section « coût du travail » de la maquette lit
     l'historique git. Ses chiffres changent à chaque commit, et la copie
     serait toujours périmée. Dans le script définitif, elle s'affiche à la
     demande, par une option, et n'entre pas dans `docs/etat.md`.
3. **Les tests sur GitHub** : un workflow qui lance la suite complète à chaque
   envoi sur `main`. Le jeton d'une session peut se voir refuser l'écriture
   sous `.github/workflows/`. Si l'envoi est refusé, retirer le fichier du
   commit, pousser le reste, et remettre le fichier au propriétaire, qui
   l'ajoutera depuis GitHub.
4. **La suite rapide**, sous deux minutes : les règles et les étapes. Mesurer
   avec `time`. Ne pas changer ce que fait `python -m pytest` sans le dire dans
   `CLAUDE.md`.
5. **`CLAUDE.md`** : une ligne qui renvoie à `docs/architecture.md` et au
   tableau de bord, à la place du renvoi à cette passation.
6. **Un repère git** `phase-0` au dernier commit (§ 12). Si le jeton refuse de
   pousser un tag, le dire au propriétaire.

## Comment vérifier, avant chaque envoi

- `pip install -e '.[dev]'` une fois, puis `python -m pytest` : la suite
  complète passe, en huit à dix minutes.
- `git diff --stat tests/temoins/` est vide : aucun résultat n'a bougé.
- `python scripts/verifier_prose.py` ne signale rien.
- Envoi sur `main` par `bash scripts/pousser.sh`, jamais autrement
  (`CLAUDE.md`).

## Ce qui vient après, et pas maintenant

- **Phase 1**, en tête : l'état « écart connu » des exemples officiels
  (§ 9.2). Aujourd'hui, `tests/test_oracle.py` exige que tous passent, ce qui
  empêche d'enregistrer un exemple qui montrerait une erreur. Puis la
  documentation rangée par nature, et le contrôle de conservation.
- **Constats à consigner** dans `veille.yaml` et la feuille de route, par une
  session qui suit la procédure de veille. Aucun n'est corrigé :
  - L. 351-4 : sept rédactions changent le droit depuis 1985 ; cinq ne sont
    pas représentées dans le modèle (annexe A.2) ;
  - D. 351-1-7 : de fin 2003 à 2010, les trimestres d'enfants s'accordaient un
    par un, un à chaque anniversaire, huit au plus ; le modèle en sert huit
    d'un coup ;
  - L. 12 b : la réduction d'activité vaut dès le 1er janvier 2011 dans le
    décret, le 1er juillet dans la loi (annexe A.1) ;
  - la loi du 3 janvier 1975 est datée du 1er juillet 1974 dans l'index ; le
    modèle la fait partir en 1975 ;
  - la feuille de route dit Destinie et TRAJECTOiRE « non publiés » : leur
    code est public ;
  - 17 des 24 règles « approchées » de la veille racontent l'erreur corrigée,
    sans dire ce qui reste.
- **À relire** sous l'angle des licences (§ 3.4) : le workflow
  `documents-apportes.yml` republie des documents publics sur une release.

## Travailler sobrement

- Lire ce fichier. De la note 0001, lire L'essentiel, les § 9 à 13, puis les
  annexes B et C. Le reste se consulte au besoin.
- Ne pas lire `feuille_de_route.md` ni `limites.md` en entier : chercher.
- Ne pas relancer de vérification de l'architecture : elle est décidée.

## Les outils laissés ici

- `tableau_de_bord.py` : la maquette du tableau de bord.
  `python docs/decisions/0001/tableau_de_bord.py . > /tmp/etat.md` l'essaie
  sans rien écrire dans le dépôt.
- `partage_fiche.py` : le contrôle du partage des versions à chaque date
  d'observation (§ 4.1). Il lit les fiches YAML d'un fichier Markdown, comme
  l'annexe A. Il servira à la phase 2.
