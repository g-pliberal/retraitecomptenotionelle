# Étape 5 : KALI, la base des conventions collectives, dans l'index

**Reprise, au 11 novembre 2026.** Rien n'est commencé. Le propriétaire a
demandé le 11 novembre d'ajouter à l'index la base des conventions
collectives de la DILA, nommée KALI, qui porte le régime Agirc-Arrco. Elle a
le format de LEGI : un dump global de 184 Mo et des incréments quotidiens. À
faire, le test d'abord : `dila_index.py kali` la construit, la met à jour, la
récupère et la publie ; `dila_cherche.py kali` y cherche, et y lit l'histoire
d'un article comme dans LEGI ; le workflow `index-dila.yml`, qui est une
garde, la publie chaque lundi. L'étape 4 retouche le même workflow : rattraper
`main` avant d'y toucher. La liste de contrôle des textes n'est pas étendue
ici. Aucune règle du scénario 1 n'est en jeu. Commencer par « Ce qu'il y a à
faire », ci-dessous.

**La demande, le 11 novembre 2026.** La session qui a mesuré les outils (note
`2026-11-11-sorties-et-temps-des-outils.md`) a proposé au propriétaire
d'« ajouter KALI à l'index », en précisant : « C'est une étape moyenne, qui
touche aussi le workflow », puis : « Plus tard, si vous le voulez : ajouter à
l'index la base des conventions collectives, qui porte les accords
Agirc-Arrco. » Sa réponse : « ajouter à l'index la base des conventions
collectives ». C'est l'accord pour le workflow, que seul GitHub peut faire
publier : une session n'écrit pas la release.

**Ce qui est su, relevé le 11 novembre 2026.**

- La base est à `https://echanges.dila.gouv.fr/OPENDATA/KALI/` : le dump
  `Freemium_kali_global_20261108-140000.tar.gz`, 184 Mo, des incréments
  `KALI_<date>-<heure>.tar.gz` chaque jour, et une présentation de la DILA,
  `DILA_KALI_Presentation_20170824.pdf`. Le serveur répond depuis une session.
- Lu en flux, par ses seuls titres, le dump porte des textes titrés « Régime
  AGIRC-ARRCO de retraite complémentaire », « Régime AGIRC-ARRCO Avenant
  n° 1 » et « Avenant n° 2 ». Aucun texte n'y est titré de la convention du
  14 mars 1947 : la note `138/2026-10-13-etape-16-coefficients-de-1947.md` le
  disait déjà. Rien d'autre n'en a été lu.
- Le dépôt cite déjà un article de KALI par son adresse sur Légifrance :
  `KALIARTI000036731850`, dans `data/sources.yaml`
  (`agirc_arrco_majorations_familiales`). La note
  `153/2026-10-16-etape-2-points-enfants-arrco.md` dit l'accord du 18 mars
  2011 « à KALI, que la session n'a pas lu ».
- `scripts/fetch/dila_index.py` et `dila_cherche.py` ne connaissent que
  `jorf` et `legi`. `lire()` ramène un fichier XML à une ligne de l'index ;
  l'index SQL des articles (`ARTICLES_DE_LEGI`) ne naît que pour LEGI.
  `perimetre.yaml` dit que la liste de contrôle ne tient pas les accords
  Agirc-Arrco, « qui ne sont pas dans l'index ».

**Ce qu'il y a à faire.**

1. *Lire la forme de KALI* avant d'écrire : la présentation de la DILA, la
   DTD (`OPENDATA/DTD_LEGIFRANCE/`), quelques fichiers du dump. Ce qu'un
   article y porte de plus ou de moins que dans LEGI : sa convention, son
   état (en vigueur, étendu ou non), ses dates.
2. *Décider du filtre*, mesure faite : la base entière, ou le champ que
   `THEMATIQUE` retient. Dire la taille de l'index dans les deux cas ; si le
   choix n'est pas évident, le demander au propriétaire.
3. *`dila_index.py kali`*, le test d'abord, sur un dump de poche à la manière
   de la fixture `legi` de `tests/test_dila_index.py` : construire, mettre à
   jour, récupérer, publier.
4. *`dila_cherche.py kali`* : la recherche plein texte, puis l'histoire d'un
   article, son mot à mot et sa version à une date, comme pour LEGI, avec ce
   que KALI demande en propre pour désigner un article : un numéro seul ne
   suffit pas d'une convention à l'autre.
5. *Le workflow* `index-dila.yml` : `kali` dans la matrice, et la release.
   Le commit porte `Garde-modifiée:` et sa raison ; l'accord est celui de la
   demande ci-dessus.
6. *La procédure* : `docs/veille_droit.md`, « Chercher dans le JORF ou
   LEGI », dit les commandes.

**Ce que l'étape laisse.** Faire entrer les accords Agirc-Arrco dans la liste
de contrôle des textes, et relire sur KALI les fiches de la retraite
complémentaire : une autre étape, que le propriétaire décidera au vu de ce
que l'index porte.

**Fini quand** : chaque comportement a son test, vu rouge puis vert ;
`python -m pytest -m rapide` et les tests de la zone passent ; l'index de
KALI est publié par le workflow, lancé une fois à la main, ou la note dit ce
qui l'empêche ; une recherche et une histoire d'article du régime Agirc-Arrco
sont montrées dans la note ; son bloc « Reprise » est ôté ; l'entrée du
journal de veille est écrite.
