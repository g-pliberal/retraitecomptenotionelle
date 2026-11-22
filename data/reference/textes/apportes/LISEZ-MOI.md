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
  droit d'auteur ne protège pas, dans notre propre transcription. Pour
  Gallica, on n'archive ni l'image ni le fichier texte de la BnF, qui réserve
  leur réutilisation commerciale ; on donne l'ark et la vue. Les fac-similés
  de Légifrance (DILA) peuvent aller sur la release, sous la Licence Ouverte,
  avec leur mention.
- **Reste à lire** : les conditions d'utilisation de Gallica. Le statut
  `libre` repose sur la notice de chaque numéro (« Public domain », « Source :
  DILA ») et sur le fait que seule notre transcription est archivée. Ces
  conditions se liront et se dateront à la prochaine session sur le poste de
  Gilles, puisque Gallica refuse le conteneur ; on reportera alors leur
  clause dans `rediffusion.texte`.
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

## Ce qui reste à transcrire

Ces six numéros ont été lus le 21 novembre 2026 au soir, mais pas encore
transcrits ici : la session de Gilles a pris fin. Les citations sont dans les
notes de lecture du fil « Lire les textes anciens au Journal officiel ».
Chacun se reprend depuis le poste, en passant par le mode texte
(`.../f<vue>.texteBrut`), une vue toutes les vingt secondes au moins. Gallica
présente une vérification Cloudflare à presque chaque page, et c'est au
propriétaire de la passer.

| Texte | JO | ark Gallica | vues |
|---|---|---|---|
| Décrets n° 54-50 (EDF-GDF) et 54-51 (mines) du 16 janvier 1954 | 17 janvier 1954, p. 662 | `bpt6k1565427m` | 6 |
| Loi du 12 avril 1941, retraites des marins | 6 mai 1941 | `bpt6k9617210s` | 3 à 5 |
| Ordonnance n° 45-170 du 2 février 1945 (AVTS) | 3 février 1945 | `bpt6k96955305` | 6 et 7 |
| Ordonnance n° 45-2454 du 19 octobre 1945 | 20 octobre 1945, p. 6721 et s. | `bpt6k2033716d` | 34, 35 et 38 |
| Loi n° 48-1306 du 23 août 1948 (assurance vieillesse) | 24 août 1948, p. 8306 et s. | `bpt6k1576644d` | 4 à 6 |
| Loi n° 48-1469 du 22 septembre 1948 (marins) | 23 septembre 1948, p. 9366-9367 | `bpt6k15690262` | 6 et 7 |

Restent aussi à prendre : la vue 4 du JO du 20 août 1936, la fin de la loi du
18 août 1936 et son tableau, et la vue 52 du JO du 10 janvier 1954, le titre et
les premiers visas du décret n° 54-23. Le JO du 21 septembre 1948, qui porte le
code des pensions de 1948, manque à Gallica : on le cherchera parmi les
fac-similés de Légifrance, après le captcha.
