# Étape 5 : KALI, la base des conventions collectives, dans l'index

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

**Ce qui a été fait, le 11 novembre 2026.** Chaque comportement par son test,
vu rouge puis vert, dans `tests/test_dila_kali.py` : un dump de poche repris
de vrais fichiers de KALI — l'article 92 de l'accord du 17 novembre 2017, les
trois rédactions de l'article 1er de l'accord du 10 mai 2019, un avenant de
salaires de la convention des coopératives de consommateurs.

- *La forme de KALI.* Celle de LEGI : des textes (`KALITEXT…`), sans corps,
  qui ne portent que titre et signataires, et des articles (`KALIARTI…`). Un
  article y porte de plus son état (`VIGUEUR_ETEN`, `VIGUEUR_NON_ETEN`,
  `REMPLACE`, `PERIME`, `ABROGE`, `MODIFIE`, `DENONCE`, `VIGUEUR`), où se lit
  qu'il est étendu ou non, et un conteneur, un seul : sa convention, avec son
  numéro (IDCC, parfois plusieurs), ou un « texte indépendant » sans numéro,
  ce qu'est l'accord Agirc-Arrco. Ses dates d'extension valent toutes
  2999-01-01 : elles ne disent rien. La date de publication d'un texte aussi :
  c'est sa validité qui le date. La base compte 352 617 documents, 307 474
  articles et 45 143 textes, dont 53 061 articles sans numéro.
- *Le filtre : la base entière.* Mesuré sur le dump du 8 novembre : entière,
  352 000 documents, 919 Mo en SQLite et 342 Mo compressés, construits en
  85 secondes ; filtrée par `THEMATIQUE`, 99 000 documents, 398 Mo et 151 Mo,
  en 190 secondes. Entière, elle pèse moins que LEGI filtré (455 Mo publiés),
  et le filtre, écrit pour le Journal officiel, y gardait surtout les salaires
  et la prévoyance des branches. La raison du filtre — une base trop grosse
  pour être publiée — ne vaut pas ici, et un index entier permet de dire qu'un
  texte n'est pas dans KALI. Le choix n'a donc pas été porté au propriétaire ;
  il tient à un mot de `BASES` (`entiere`), et se défait en le retirant.
  Avec ses quatre colonnes et son index SQL, l'index pèse 1 010 Mo, et
  276 Mo une fois compacté et compressé pour la release.
- *`dila_index.py kali`* construit, met à jour, récupère et publie. L'index
  de KALI porte quatre colonnes de plus, `etat`, `cid` (le texte qui porte
  l'article), `idcc` et `convention` ; ceux du JORF et de LEGI gardent leurs
  sept colonnes, un test le tient.
- *`dila_cherche.py kali`.* Chaque ligne ajoute, entre parenthèses, l'état,
  le numéro de la convention et le texte de l'article. `--dans KALITEXT…` et
  `--idcc N` bornent une recherche. L'histoire d'un article, son mot à mot et
  sa version à une date se demandent par `--num` et `--dans` : un numéro seul
  est refusé — 24 917 textes ont un article 1 ou 1er —, et les versions se
  groupent par l'identifiant du texte, non par son titre, que 1 543 titres
  partagent entre plusieurs textes.
- *Le workflow* : `kali` dans la matrice de `index-dila.yml`, et trois lignes
  de son en-tête ; rien d'autre de la garde. `--publier` relit la release
  après l'envoi, avant d'y écrire sa ligne : trois bases publient désormais en
  même temps, et chacune remettait la ligne périmée des autres.
- *La procédure* : `docs/veille_droit.md`, « Chercher dans le JORF ou LEGI ».

**Le régime Agirc-Arrco, montré.** `dila_cherche.py kali '"valeur de service
du point"' --titre agirc-arrco` rend 23 documents en un dixième de seconde,
dont :

```
KALIARTI000039097693  2019-01-01 → 2021-10-13  Article Accord art. 1er  Accord national interprofessionnel du 10 mai 2019 relatif au régime AGIRC-ARRCO de retraite complémentaire  (remplacé ; dans KALITEXT000039097685)
    La [valeur de service du point] a été fixée au 1er novembre 2018 à…
```

et `--num 1er --dans KALITEXT000039097685 --diff`, l'histoire de cet article,
ses trois rédactions et ce que chacune change :

```
KALIARTI000039097693  2019-01-01 → 2021-10-13  … (remplacé ; dans KALITEXT000039097685)
KALIARTI000047193923  2021-10-13 → 2022-10-25  … (remplacé ; dans KALITEXT000039097685)
    … 1er novembre 2018 à 1,2588 €. [-Durant la période couverte par le présent accord (2019,-]{+Pour les exercices 2019 et+} 2020, [-2021 et 2022),-] la valeur de service du point …
KALIARTI000047194783  2022-10-25 → 2022-12-31  … (périmé ; dans KALITEXT000039097685)
    … tactique visé à l'article 6 ci-après. {+Dans l'hypothèse où l'évolution des prix est supérieure à celle des salaires, la valeur de service du point évolue comme les salaires, …+}
```

L'accord du 17 novembre 2017, qui fonde le régime, est `KALITEXT000036731682`,
en vigueur étendu ; son article 92, `KALIARTI000036731850`, celui que
`data/sources.yaml` cite, n'a qu'une rédaction. Cinq textes portent « 14 mars
1947 » dans leur titre, aucun « 8 décembre 1961 ».

**Le workflow, lancé une fois à la main**, le 11 novembre 2026 à 23 h 56 UTC
(course n° 15, sur le commit du code) : les trois bases en vert. KALI, que
rien ne publiait encore, s'est construit du dump et a été publié en cinq
minutes : `kali.sqlite.gz`, 276 Mo, 352 617 documents, à jour au 10 novembre
— la DILA n'avait pas d'incrément du 11 pour KALI. `dila_index.py kali
--recuperer` le rend en 14 secondes depuis une session, et l'article 92 s'y
lit. La release porte ses trois lignes, celles de LEGI et du JORF intactes.
LEGI et le JORF ont pris l'incrément du 11 ; l'inscription de l'étape 4 n'a
rien trouvé de neuf.

**La DILA a renouvelé ses dumps le 8 novembre 2026**, ceux des trois bases,
et retiré les incréments d'avant : le 11, chaque répertoire ne listait que le
dump du 8 et les incréments parus depuis. Un index arrêté avant un dump neuf
ne peut plus rattraper ce qui a paru entre son dernier incrément et ce dump.
Pour KALI, `--mettre-a-jour` reconstruit alors l'index depuis le dump neuf, en
quelques minutes, et le dit. Pour le JORF et LEGI, rien n'est changé : leurs
index publiés le 9 novembre, à jour au 8 à 21 h 04, ont enjambé ce
renouvellement sans trou, mais la prochaine fois la mise à jour appliquerait
les incréments restants et publierait un index troué sans le dire.

**Les limites.** Un article sans numéro ne se suit pas de version en version :
il se lit par `--texte`. Dans 3 663 cas sur 218 431, un même numéro désigne
deux articles en vigueur d'un même texte, d'une annexe à l'autre : leurs
histoires se mêlent alors. Le titre propre d'un article (« Valeur de service
du point ») n'est pas indexé. Le format des listes de suppression de KALI est
repris de celui du JORF, aucun des deux incréments lus n'en portant.

**Ce qui reste, et qui revient au propriétaire.**

- Les accords Agirc-Arrco dans la liste de contrôle des textes, et la
  relecture sur KALI des fiches de la retraite complémentaire : l'étape que
  cette note laissait. `perimetre.yaml` dit encore que ces accords « ne sont
  pas dans l'index ».
- Ce que la mise à jour du JORF et de LEGI doit faire quand la DILA a
  renouvelé un dump avant que l'index l'ait rattrapé : refuser, pour que le
  workflow s'arrête et qu'on le relance en cochant « reconstruire » (une heure
  à une heure et demie sur GitHub), ou reconstruire d'elle-même. La détection
  existe, pour KALI, dans `mettre_a_jour`.
