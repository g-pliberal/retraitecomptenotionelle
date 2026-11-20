# Les compteurs de l'étape 1, repris sur leurs trois raccourcis

Le 20 novembre 2026, le propriétaire demande que les nombres posés à
l'étape 1 de la note de décision 0009 mesurent le chemin qui reste. La note
du 19 novembre, « Étape 1 : les cinq cliquets », signalait trois raccourcis.
Cette session les reprend un à un. Aucune règle, aucune fiche, aucun fichier
de régime ne change, et aucun résultat ne bouge : elle ne touche que
`tests/test_cliquets_du_droit_date.py`, `tests/outils_droit_date.py` et la
liste `tests/cliquets_du_droit_date/constantes.yaml`.

**Les chiffres de la loi dans le code : le relevé ne voyait que les dates.**
Le cinquième cliquet relevait les constantes dont la valeur porte une date ou
une année. Un âge, un taux, une durée n'en ont pas : ils s'ajoutaient « à la
main », et un seul l'avait été, `SURCOTE_AGE_MAJORE`. Le relevé prend
désormais aussi toute constante nommée dont la valeur écrit un nombre sans
date (`constantes_chiffrees`). Il en trouve 161 dans le moteur hors du site,
quatre fichiers sans règle écartés en entier (les fonctions mathématiques, la
lecture d'un PDF, l'écriture des nombres, le journal), que la liste nomme. 63
sont du droit des retraites : les 16 points du plancher agricole, les 37,5
années du minimum, le coefficient plancher de 0,43, les paliers de
l'anticipation, les seuils du minimum garanti, les parts de SMIC du cumul.
98 n'en sont pas : 43 du calcul, 34 de la saisie et du relevé lu, 8 de
l'impôt, 8 réglages, 2 des prélèvements sociaux, 2 de projection, une de la
rémunération.

Le cliquet passe ainsi de 113 à 175 constantes du droit à migrer, et de 67 à
104 sans fiche désignée. Rien n'est entré dans le code : le chemin était plus
long que le nombre ne le disait. Une constante chiffrée neuve que la liste ne
classe pas fait désormais échouer la suite, comme une constante datée.

**Comment elles sont classées.** Sur la déclaration et son commentaire ; pour
la vingtaine qui n'en avait pas, sur le code qui la lit. Les 45 constantes
datées classées « hors » le 19 novembre ont été relues de même, et aucune ne
change de classe. Les textes n'ont pas été relus : dire qu'un nombre est du
droit des retraites ne le demande pas, dire de quelle fiche il relève le
demande. Les 104 sans fiche restent donc « à désigner » par l'étape qui migre
leur règle, comme le prévoyait la note du 19 novembre : c'est déjà le travail
des étapes 2 à 4, cette session ne le double pas. Trois classements se
discutent, et sont comptés du droit : l'année de 360 jours des pensions
(`droit/compter.js`), les bornes des assiettes en plafonds (`regimes.js`), les
abattements du micro-entrepreneur (`saisie.js`).

**Ce que le relevé ne voit toujours pas.** Un nombre écrit en clair dans une
expression, sans nom : `points < 16.0` dans le corps d'une fonction. Rien ne
le distingue d'un rang ou d'une unité, et le relever demanderait de lire
chaque fonction. L'étape qui migre une règle lit sa fonction : c'est elle qui
les trouve.

**Les renvois sans texte cité : déjà prévu, rien à faire.** La note du
19 novembre disait que le champ manquait. Il existe depuis la correction de la
surcote de la Banque de France, le même jour : `textes_des_renvois`, que
`texte_cite` lit. Le cliquet reste à 306 parce qu'aucun des renvois d'avant ne
le remplit. Les remplir est l'étape 4 de la note, qui date chaque renvoi au
jour de son texte et le cite : le nombre mesure bien ce qui lui reste.

**Les preuves des versions : un second nombre, pour la lecture.** Le quatrième
cliquet tient la première preuve pour acquise quand la version se dit `lue` et
cite un texte. Le moteur lit aujourd'hui 264 versions, dans 54 fiches ; 237
n'ont pas leurs deux preuves ni ce qui manque, presque toutes faute d'avoir
écrit ce qui a été cherché comme exemple. Ce nombre tomberait donc à zéro en
remplissant un champ, sans qu'aucun texte soit relu.

Un second nombre le garde : parmi les 213 versions `lue`, 153 citent au moins
un texte sans date de lecture (`lu_le`) ni citation exacte (`citation`), les
deux traces que le contrat des fiches sait garder d'une lecture. Il ne peut
que baisser (`VERSIONS_LUES_SANS_TRACE`). Il ne prouve pas la lecture : seule
une relecture la vérifie, celle que le second rectificatif demande pour les
versions sans exemple qui décident de pensions. Il dit combien de versions
sont à relire avant que « lue » veuille dire quelque chose, et une version
relue en sort en datant chacun de ses textes.

Les identifiants cités ont aussi été confrontés à la liste des rédactions du
dépôt : sur 612 textes cités par ces versions, 543 y sont ; les autres sont
des textes du Journal officiel, des statuts de caisse ou des articles du code
général de la fonction publique, que la liste ne suit pas. Aucun identifiant
n'est faux.

**Au propriétaire.** Relire 153 versions est un chantier, non une retouche :
il se mène avec les étapes qui migrent chaque fiche, ou à part, par poids dans
les résultats. Le nombre est posé pour qu'il se voie.

**Ce que la session a coûté.** Un commit, quatre fichiers dont cette note.
Les treize tests du fichier sont verts, la suite rapide aussi.
