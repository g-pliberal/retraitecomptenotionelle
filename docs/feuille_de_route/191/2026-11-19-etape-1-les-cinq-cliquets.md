# Étape 1 de la note 0009 : les cinq cliquets et la garde de l'âge du taux plein

Le 19 novembre 2026, le propriétaire ouvre l'étape 1 de la note de décision
0009. Sa première session pose les cinq cliquets de la note et la garde que
le second rectificatif leur joint. Aucune règle, aucune fiche, aucun fichier
de régime ne change, et aucun résultat ne bouge : l'étape n'ajoute que des
tests, `tests/test_cliquets_du_droit_date.py`, ce qu'ils comptent,
`tests/outils_droit_date.py`, et une liste,
`tests/cliquets_du_droit_date/constantes.yaml`. Le sixième cliquet, l'alarme
« loi modifiée », est la seconde session de l'étape.

**Ce que chaque cliquet compte, au 19 novembre.** Chaque nombre est posé dans
le test. Il échoue quand le nombre monte, et aussi quand il baisse, pour que
la session qui l'a fait baisser l'abaisse.

1. *Les valeurs de repli.* 1 442 valeurs écrites dans une période à côté du
   renvoi qui les remplace : 562 âges d'ouverture, 469 âges du taux plein,
   411 durées requises.
2. *Les renvois sans texte cité.* 306 renvois, comptés en séries : un champ
   qui renvoie à la même fiche de période en période n'en fait qu'un. 131
   commencent à la première période de leur régime, 175 plus tard, ce que le
   rectificatif comptait en 173 débuts et 2 changements de fiche. Aucun ne
   cite de texte.
3. *Les copies d'avant réforme.* Les quatre que la note nomme sont là. Six
   autres tables portent « avant » dans leur nom et sont du droit, non des
   copies : le test les nomme aussi, et une table de ce nom qui naîtrait sans
   y être déclarée le fait échouer.
4. *Les versions sans leurs preuves.* Des 243 versions que le moteur lit,
   dans 54 fiches, 238 n'ont pas leurs deux preuves. Cinq les ont.
5. *Les chiffres de la loi dans le code.* Le relevé trouve 163 entrées dans
   le moteur hors du site : 132 constantes nommées dont la valeur porte une
   date ou une année, et 31 années écrites en clair, sur 40 lignes. La liste
   en classe 118 comme du droit à migrer et 45 hors du droit des retraites :
   30 de l'impôt sur le revenu, 9 de la saisie, 2 d'une carrière type, 2 de
   la rémunération des agents publics, un réglage, une sentinelle. Avec
   `SURCOTE_AGE_MAJORE`, ajoutée à la main parce qu'elle est sans date, le
   cliquet est à 119.

**La garde.** `tests/test_droits_contrefactuels.py` contrôle désormais l'âge
auquel la décote s'annule, sous les trois états du droit et pour les cinq
générations du fichier : 67 ans. La valeur vient de l'article L. 351-8, 1°,
relu dans l'index LEGI le jour même : « l'âge prévu à l'article L. 161-17-2
augmenté de cinq années » du 22 janvier 2014 au 31 août 2023, soit 62 ans
plus cinq ; « augmenté de trois années » depuis le 1er septembre 2023, soit
64 ans plus trois, sous la loi de 2023 comme sous la suspension. Le test a
été vu rouge en lui demandant 65 ans, quinze fois « 67,0 », puis remis à 67.

**Ce que les tests ne voient pas encore.** Quatre choses sont à savoir avant
de lire ces nombres comme une mesure du droit.

- Le schéma des régimes n'a aucun champ où une période cite le texte de son
  renvoi. Le cliquet 2 compte donc tous les renvois. L'étape qui date et cite
  les renvois crée ce champ, et le fait lire à `texte_cite`.
- Le contrat des fiches n'a pas d'endroit où une version dit ce qui a été
  cherché et ce qui manque. Le cliquet 4 ne compte donc que les deux preuves.
  La première est tenue pour acquise quand la version est « lue » et cite ses
  textes : c'est une déclaration de la fiche, non une vérification. La
  seconde est une liste d'exemples publiés.
- Une constante du droit n'est rattachée à une fiche que si la fiche la nomme
  elle-même, dans son champ `code.javascript` : 51 le sont, et le test le
  vérifie. Les 68 autres sont « à désigner » par l'étape qui migrera leur
  règle. Les deviner d'après la fonction qui les lit donnait des fiches
  fausses.
- Le classement « droit » ou « hors du droit » s'est fait sur le nom, la
  valeur et le commentaire de chaque constante, sans relire les textes. Les
  fichiers entiers de l'impôt, de la saisie et du relevé lu sont classés
  hors.

**L'écart avec l'évaluation du 18 novembre.** Elle comptait 131 constantes.
Son relevé gardait les libellés, coupait une déclaration à sa septième ligne,
et ne voyait ni les constantes posées après leur classe
(`MinimumGaranti.ANNEE_GEL`) ni les générations à décimales (`1961.667`). Le
relevé du test les prend, et compte à part les années en clair du reste du
code.

**Ce que l'étape a coûté.** Un commit, cinq fichiers, dont cette note, et une
session d'un peu plus de vingt minutes d'horloge après le feu vert, selon
son journal, la mesure du sixième cliquet non comprise. La suite rapide est
verte avant l'envoi.

**Ce qui attend.** La seconde session de l'étape, pour le sixième cliquet.
Puis les étapes de la note, qui font baisser ces nombres une à une.
