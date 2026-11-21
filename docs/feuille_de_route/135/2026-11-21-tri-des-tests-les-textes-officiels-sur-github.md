# Le tri des tests : les textes officiels et les fichiers de la DREES, sur GitHub

Le 21 novembre 2026, à la suite de l'audit de la suite demandé par Gilles
(rapport et patchs dans le dossier du projet, `architecture/tri-des-tests/`),
et avec son accord (« Tout : patchs et tests sur GitHub »).

Soixante-dix tests relisent nos valeurs dans les textes officiels, par
l'index LEGI et JORF de la DILA, ou dans les fichiers de la DREES, dont le
panorama de 2026 en PDF, que `pdftotext` lit. La suite complète
de GitHub ne les jouait jamais : `data/brut/` y est vide, et ils se
sautaient. Seules les sessions qui avaient récupéré ces fichiers les
jouaient, et un texte qui changeait sous une valeur du dépôt ne se voyait
pas.

Chaque tranche de la suite (`.github/workflows/tests.yml`, travail `suite`)
récupère désormais, avant de lancer pytest, `pdftotext` (le paquet
`poppler-utils`), l'index LEGI et l'index JORF
(`scripts/fetch/dila_index.py <base> --recuperer`), et les fichiers de
`data/brut/` qui ont un miroir (`scripts/fetch/source_locale.py --recuperer`),
tous publiés sur les releases du dépôt, qui est public : aucun jeton. Ce qui
manque ne fait pas tomber la tranche : ses tests se sautent comme avant, et
un avertissement de la course le dit. Aucun cache : près de quatre gigaoctets
en chasseraient la mémoire des calculs. `tests/test_outillage.py` tient
l'étape.

Un défaut trouvé en chemin : la fixture `donnees_d_ailleurs` de
`tests/test_pont.py` copiait tout `data/`, `data/brut/` compris. Avec l'index
de la DILA, chacun de ses trois tests recopiait près de cinq gigaoctets : le
21 novembre, une suite rapide en a laissé vingt dans le dossier temporaire de
pytest, et le disque de la session s'est rempli. Sur GitHub, la tranche qui
porte ces tests aurait fait de même. La copie laisse désormais `data/brut/`,
que le paquet ne lit pas ; un test le dit.

Vérifié ici, avec l'index publié et les fichiers récupérés : les dix fichiers
qui portaient ces tests passent en entier, sans aucun test sauté (554 tests,
en une minute et demie).

Reste :

- la première course de GitHub dira ce que l'étape coûte à chaque tranche, en
  temps et en disque ;
- `scripts/filets.py` copie lui aussi tout `data/` dans chaque processus de
  sa neutralisation : dans une session qui a récupéré l'index, il en
  copierait autant de fois les quatre gigaoctets. Il ne tourne pas sur
  GitHub ; la même exclusion lui irait.
