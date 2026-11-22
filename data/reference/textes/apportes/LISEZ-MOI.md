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
| `JORF_19480118_16.pdf` | loi n° 48-101 | `f399e021689fc7c3e332a22d0e74dbfd9352e043b13bb60ec56ba140d601f4b5` |
| `JORF_19490402_80.pdf` | décret n° 49-456 | `8c1f1d3d2eaab6e8dc128cb2b7092639a547c75a86651c61e45097308f75a0d8` |
| `JORF_19620415_91.pdf` | décret n° 62-439 | `cfc77a0f920defa90314565e7c3ae72e54ffee7e9f95730732dd0062da79dfa9` |
| `JORF_19790511_109.pdf` | décret n° 79-372 | `13db19ade00fadbdbb206d44414bc277627ac08993a2fec216a4727763c89c03` |
| `JORF_19800611_135.pdf` | décret n° 80-404 | `04666eb1e410db493fc4573d17a9fcc07e68d8e86ec603258a350c680f5eef3e` |
| `JORF_19800621_144.pdf` | décret n° 80-439 | `36f856afc458696063bccdc4821c9b30b384d91ad954efd960daf4dcc7981a54` |
| `JORF_19810908_210.pdf` | décret n° 81-828 | `ba63a8138b6dba480899200b6d1d7a4c564a16fb254c81d1481162202eef17b3` |
| `JORF_19810909_211.pdf` | décret n° 81-831 | `2981dbea597b7821990268f6bd225b23874c93bae7bb9a1f345cc64bf9558248` |
| `JORF_19820804_179.pdf` | décrets n° 82-674 et 82-678 | `9fbfe5a4efe30ed4c1443057ff106b72d3101cc42ae700a02357a3c3d89d7306` |
| `JORF_19830710_159.pdf` | décret n° 83-619 | `3c2831232b82727a255bebd3a1a735ee902a8bbd37c48932aadaeeb92dfd4f10` |
| `JORF_19830717_164.pdf` | décret n° 83-651 | `7155377d2bb1dddc679f4a027c1e8e23a040a3cab840cf5fee74318e6224e08e` |
| `JORF_19830727_172.pdf` | décret n° 83-677 | `98f87650d6c0dd28219c887762a6eef76c6e915459648c75d759da3a84db5b9f` |
| `JORF_19890517_113.pdf` | décret n° 89-313 | `898e7a288eb180bb4d9621e6b42ea4d8061a3bd551169d10121883ba42fa636f` |
| `JORF_19680630_153.pdf` | décret n° 68-579 | `4d41c2c99eb54087839d965ceafd906c46f80001eeb14658386447ce8e710e7e` |
| `JORF_19760804_180.pdf` | décret n° 76-727 | `4ba375f9772337bb77c937d6f0313b9f079bf59808fff4f48611ee937c2e8f61` |
| `JORF_19770630_150.pdf` | décret n° 77-677 | `9ba522c1ea11b74d374c29db7d98b0b7ab84e1d7ce1c67156a6c0f09cbc34205` |
| `JORF_19770826_197.pdf` | décret n° 77-966 | `d7db0227416ee1a4321d704e974094f5daa0ee4913a39dc0c7d859574e74ac9b` |
| `JORF_19811114_267.pdf` | décret n° 81-1015 | `e1b8e49f403f35fd57f196300fa4d2e409348c7baa4d55906049405917cacd3d` |
| `JORF_19960208_33.pdf` | décret n° 96-101 | `9a82d0b459d78a8b8e0f666b3da86b1b16c495bedca05f1297eab2d4faf8ec3e` |
| `JORF_19980912_211.pdf` | décret n° 98-809 | `62a2ad1461bb949d08c73b462406719a33d689eabb863457fba9906e9be05836` |
| `JORF_19981009_234.pdf` | décret n° 98-896 | `9b50f7e2825245ce60594702c99e8babd582f636189baab219639456f95ee5fc` |
| `JORF_19520711_166.pdf` | loi n° 52-799 | `438dad0503a9502358a5f1173534fde323921027e30bf22074aa351399e93013` |
| `JORF_19640924_223.pdf` | décret n° 64-994 | `446e6483a1240d6cc521575a9069087909c9a1c90109ccc41a22c8610692edd2` |
| `JORF_19660422_94.pdf` | décret n° 66-248 | `12459c9459fc198533e0e8318d20658bf45c93dc5e253f16152e72db2d831393` |
| `JORF_19670718_165.pdf` | décret n° 67-570 | `d7b18ec7a52d60a0ab354f582922d5f90279871eea185d6baf4c1a59de1469c0` |
| `JORF_19680627_150.pdf` | décret n° 68-571 | `89fba562d9c77d975d16249fd7a8a02c7afc6b021bd6489804d24d7aec88c0cd` |
| `JORF_19710331_76.pdf` | décret n° 71-239 | `f3a17052cca0a2a9a6b7bd1eeff472ce6aed6f839d1dcc59b0d06dce93121a1e` |
| `JORF_19740517_117.pdf` | décret n° 74-443 | `c9a361afcb4f7de9f08cb2c1e41ee6119685e89593587e7a590b1fb3260b5c5c` |
| `JORF_19810820_194.pdf` | décret n° 81-790 | `962e6db7c78f909934ef5ddd1f5e3db200d856852deef2616adfd3645f803e74` |

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
- Tous les numéros téléchargés le 22 novembre 2026 sont transcrits, dont
  les treize textes des professions libérales (régime d'allocation de 1948 à
  1983, cotisations de la Cipav et de la CAVEC de 1979 à 1989), les huit des
  agricoles, des artisans et des commerçants (loi n° 52-799, décrets n° 64-994,
  66-248, 67-570, 68-571, 71-239, 74-443 et 81-790) et les huit du taux
  maladie (n° 68-579, 77-677, 81-1015), des majorations des salariés agricoles
  (n° 76-727, 77-966) et des tableaux de reclassement de la fonction publique
  (n° 96-101, 98-809, 98-896).
- Du décret n° 96-101, les visas et les articles 1er, 2 et 4 à 36.
- De la loi n° 52-799, le titre Ier (allocation des non-salariés non
  agricoles) et les articles 23 à 48 ; des décrets n° 64-994 et 66-248, les
  articles qui ne touchent ni aux classes, ni aux points, ni aux conjoints
  (`articles` dit lesquels sont transcrits).
- Aucun numéro de mai 1946 n'a été téléchargé : l'arrêté du 14 mai 1946
  reste à prendre sur Légifrance.
