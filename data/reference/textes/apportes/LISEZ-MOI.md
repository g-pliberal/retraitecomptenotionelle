# Les textes apportés

Ce dossier garde les textes que le dépôt ne lit que depuis le poste du
propriétaire : le Journal officiel ancien sur Gallica, derrière Cloudflare,
les fac-similés du JO sur Légifrance, derrière un captcha. Une fois
transcrit ici, un texte se relit sans ce poste.

## Le format

Un fichier par texte, `<texte>.md`, dont le nom est la clé. Il commence par un
en-tête YAML, puis vient le corps, c'est-à-dire le texte lui-même :

- `texte`, `titre`, `publication` (le numéro du JO et la page) ;
- `source` et `adresse`, avec l'identifiant ark et la vue pour Gallica ;
- `vues` et `articles` : ce qui est transcrit, et rien de plus ;
- `versions` : les versions des fiches que le texte fonde, en
  `<fiche>#<version>` ; le test vérifie que chacune existe ;
- `lu_le`, la date de lecture, et `etabli`, la façon dont le texte a été établi
  (depuis l'OCR ou depuis l'image) ; `confrontee_a_l_image`, vrai ou faux, dit
  si la transcription a été relue mot à mot sur l'image ;
- `sha256`, l'empreinte du corps : un corps retouché sans elle fait échouer le test ;
- `rediffusion` : `statut`, toujours `libre` ici, `texte`, qui cite ce qui
  fonde ce statut, `lu_dans`, `lu_le` et `mention`, comme dans
  `data/sources.yaml` ;
- `pdf`, facultatif : `miroir`, l'adresse de l'asset sur la release
  `documents-apportes`, `sha256`, et `mention`, que la Licence Ouverte exige
  (« Journal officiel de la République française, fac-similé, Légifrance,
  DILA », avec la date de téléchargement) et que la ligne de la release
  reprend. Un PDF ne va jamais dans git. Le
  propriétaire le dépose à la main sur la release, puisque le workflow ne peut
  pas aller le chercher derrière un captcha.

Entre crochets, dans le corps, ce sont les notes du dépôt (une vue non
transcrite, une coupure), pas le texte. `tests/test_textes_apportes.py` tient
le format.

## Ce qui entre et ce qui n'entre pas

Le dépôt est public : n'entre ici qu'un texte que l'on peut rediffuser
librement.

- **Entrent** les lois, ordonnances, décrets et arrêtés publiés au JO, que le
  droit d'auteur ne protège pas, dans notre propre transcription, article par
  article.
- **Les fac-similés de la DILA, sur Légifrance**, sont la source depuis le
  22 novembre 2026. Chaque numéro ancien n'y est qu'en PDF, derrière un
  captcha que le propriétaire passe, et ce PDF **ne se republie pas** :
  Légifrance avertit qu'il contient des « informations nominatives »
  (nominations, naturalisations), dont la réutilisation est encadrée par
  l'article L. 322-2 du code des relations entre le public et
  l'administration. Le PDF reste sur le poste du propriétaire ; son empreinte
  est dans le tableau plus bas. Le champ `pdf` n'est donc pas employé pour ces
  numéros.
- **Gallica** : ses conditions d'utilisation (lues le 22 novembre 2026)
  laissent libre la réutilisation non commerciale, avec la mention « Source
  gallica.bnf.fr / BnF », mais rendent payante l'utilisation de ses documents
  et de son OCR « dans le cadre d'un projet en Intelligence artificielle »,
  hors recherche académique. Le propriétaire a choisi, le même jour, de ne
  plus transcrire depuis Gallica. Les deux textes qui en venaient (1936,
  1954 RATP-SNCF) ont été repris le 22 novembre 2026 sur les fac-similés de
  la DILA, et ne doivent plus rien à Gallica.
- **N'entrent pas** :
  - les circulaires et documents de la base de législation de la Cnav, dont
    les mentions légales (lues le 21 novembre 2026) interdisent toute
    reproduction non autorisée et n'autorisent l'extraction que d'une partie
    non substantielle (CPI, L.122-4 et L.342-3). Le registre de ses
    références, dans `data/reference/legislation/cnav/`, reste, par décision
    du propriétaire du 21 novembre 2026 ; seules de courtes citations s'y
    ajoutent ;
  - les réponses d'info-retraite, en attente de décision ;
  - les documents du COR autres que les notes de séance, dont la reproduction
    demande l'accord de leur auteur ;
  - les pages des caisses (Agirc-Arrco, statuts lus sur leur site), tant que
    leur licence n'est pas lue ;
  - Légifrance consolidé, qui n'a pas à être archivé : le dépôt le lit déjà
    dans les fichiers de la DILA.

## Les fac-similés lus

Téléchargés le 22 novembre 2026 depuis Légifrance, gardés sur le poste du
propriétaire (dossier Téléchargements).

| Fichier | Texte | sha256 |
|---|---|---|
| `JODEF_19410506_125.pdf` | loi du 12 avril 1941 (marins) | `a26c276a662efc6d7e14b71097b465d92f0eba60261f001c9d1c238549f00838` |
| `JORF_19450203_29.pdf` | ordonnance n° 45-170 | `405e5ac008a023dc09c8142d83578016d11d66fcee8e793d507f40f4ca57f55a` |
| `JORF_19451020_247.pdf` | ordonnance n° 45-2454 | `0cb9760e3c210e7ceb0bd537cb19670979e8aae94f2b86bba83e13f265975a31` |
| `JORF_19480824_200.pdf` | loi n° 48-1306 | `9e62c8719db3ebd67d6d8a399bd5a1cd0f54c0579268cdae6dd5ef32c575aa8c` |
| `JORF_19480923_226.pdf` | loi n° 48-1469 | `3155df3d506654a348004c2a27d7a06b2b840954f4360b9827e08ba442d216ce` |
| `JORF_19540117_13.pdf` | décrets n° 54-50 et 54-51 | `5b782849e4b163a65171d7e2ec046b6ec2ecc692ac2086e20b8473784b3f863e` |
| `JORF_19451230_309.pdf` | décret n° 45-0179 | `d67ed7aa33c0e490cd748d7a487320e4caf8a43d547db77e6d402f0c008e250f` |
| `JORF_19620331_78.pdf` | arrêté du 27 mars 1962, accord Arrco du 8 décembre 1961 | `22dd8648f9947558f9b908be28160c2a5d787d63af868994c6243cc84bc0ea73` |
| `JORF_19621225_303.pdf` | loi n° 62-1529 | `73a611dac28852ec889deab93166cdb10ddfeab96b40f671837fdf5fba33d1c8` |
| `JORF_19360820_194.pdf` | loi du 18 août 1936 | `54633d4e803930664adb2df5ac4b28f26185a4172e15d4da0232075d115d6edb` |
| `JORF_19480921_224.pdf` | loi n° 48-1450 | `9c2c8534d502f062536390950fa6b190983896a5070c63a42f9b1e340769324a` |
| `JORF_19540110_7.pdf` | décrets n° 54-23 et 54-24 | `027aa868d76244826f7fdcb8c17dd29557f0f8f9a9dbb754ecc1debd7806c1ee` |
| `JORF_19700807_182.pdf` | décret n° 70-717 | `15fe4f105914cc52927f3ed6dc1d6f9fc760a70dd05a0c115f446b9b3d4ba2c5` |

Le fac-similé d'un numéro se rouvre depuis la page du texte sur Légifrance
(`adresse`), bouton « Télécharger le Journal officiel… (version papier
numérisée) », après le captcha.

## Ce qui reste à transcrire

- Des longues lois, seuls les articles qu'une version cite sont transcrits ;
  `articles` dit lesquels, et le corps marque les coupures entre crochets.
- Du code des pensions de 1948 (loi n° 48-1450), les retenues (art. 4 et 5),
  les articles des militaires, des ayants cause, des cumuls et des pensions
  concédées sous la loi du 14 avril 1924 (9, 10, 12 à 15, 19 à 23, 28 à 63,
  66 à 70).
- Les vingt-neuf autres numéros téléchargés le 22 novembre 2026, lot par lot ;
  leur liste et ce que chacun sert sont dans les fichiers du projet, pas dans le dépôt.
