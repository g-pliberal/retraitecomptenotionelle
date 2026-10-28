# Étape 4, suite de la quatorzième partie : la catégorie de la pension d'invalidité, que le formulaire demande et que la saisie passe à la chronologie

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le point « Au site » du bloc de l'étape
« la catégorie », détaillé au point 3 du « Ce qui reste » de la quatorzième
partie (`2026-10-24-etape-4-plancher-de-la-pension-substituee.md`) — le champ
de la catégorie de la pension d'invalidité, que la saisie passerait à la
chronologie (`invalidite.categorie`), qui la lit depuis le 24 octobre. Ce
point seul, à la suite des études, de l'enfant né après le départ et des
révisions.

**Ce qui est fait.**

- *La saisie* (`saisie.js`) : le champ `categorie_invalidite`, 1, 2 ou 3, nul
  quand il n'est pas dit. `invaliditeDeclaree` le passe à la chronologie
  (`categorie`) avec la pension datée, et seulement quand il est dit : sinon,
  la présomption `categorie_de_la_pension_d_invalidite` le pose, comme avant.
  La saisie refuse une catégorie sans la date de la pension, même quand une
  période d'invalidité qui finit la carrière la présume (la pension présumée
  n'a pas de fait qui la porterait), une catégorie hors des trois de
  L. 341-4, une réponse qui n'est pas un nombre ; l'adresse la rend telle
  qu'elle est dite. Le contexte n'a rien à changer : il passe déjà la
  déclaration aux deux chemins de la carrière, le parcours et le relevé.
- *Le formulaire* (`pages.js`) : dans le dépliant « Invalidité, inaptitude et
  taux plein », sous « Pension d'invalidité, depuis », le menu « Catégorie de
  la pension d'invalidité » — présumée selon l'activité, première, deuxième ou
  troisième, chacune résumée des mots de L. 341-4 —, avec l'indication « si
  elle a commencé avant juin 1983 » : après, la pension de vieillesse n'a que
  l'AVTS pour plancher, et la catégorie ne compte pas. La bulle dit le
  plancher, les taux de chaque catégorie, 40 % en deuxième et en troisième
  jusqu'en mars 1961, et la présomption.
- *Les tests* : `test_invalidite.py` — la saisie lit la catégorie et la rend à
  l'adresse, cinq refus ; la carrière que le portage bâtit en porte la
  catégorie dans les deux moteurs ; l'ex-invalide de 1975, sa pension portée à
  sa pension d'invalidité refaite à la main, présumée de deuxième catégorie ou
  dite de troisième, et laissée à sa pension de vieillesse dite de première ;
  les deux moteurs confrontés étape par étape sur la pension de 1982 dite de
  troisième puis de première. `test_web.py` — deux refus et une voisine qui
  calcule ; le budget de mots du simulateur tout déplié, de 7 350 à 7 362, le
  libellé et l'indication du champ. `test_web_saisie.py` — le menu, sous la
  pension, rendu tel qu'il est dit.
- *Les témoins* : de simulation, `invalidite_substituee_en_1980_premiere_categorie` ;
  de page, `simuler_invalidite_categorie`, au formulaire entier, la troisième
  catégorie, que la ligne du plancher dit. La fabrique de GitHub les refait.
- *Le vocabulaire* : la présomption `categorie_de_la_pension_d_invalidite`
  disait que le formulaire ne demande pas la catégorie ; elle dit qu'il la
  demande, avec la date de la pension.

**Les mesures.** L'ex-invalide né en 1920, invalide depuis 1975, substitué le
1er avril 1980 : sa pension du régime général, 4 498,07 € par an à cette date,
est portée à sa pension d'invalidité de deuxième catégorie présumée,
4 778,24 €, refaite à la main ; dite de deuxième ou de troisième, de même, la
ligne du plancher le disant sans présomption ; dite de première, elle reste à
4 498,07 €, et sa pension de tous les régimes en juillet 1982 passe de
7 452,63 € à 7 065,54 € (− 5,2 %). Dans Chromium, aux cinq largeurs de
`test_ecrans.py`, dépliants fermés et ouverts, le simulateur vierge et celui du
témoin de page ne débordent pas, ne chevauchent aucune case et ne lèvent aucune
erreur ; la seule alerte est celle qu'`ALERTES_ADMISES` déclare. Ici, sur le
paquet et les témoins périmés, échouent avant comme après ces commits les sept
confrontations de `-m rapide` (le pont, les coupures au mois, la surcote
parentale, le cycle de vie) et, dans les fichiers du site, les témoins du
portage (102 écarts sur 909 cas), les carrières tirées au hasard, le paquet et
la page des données.

**Ce qui reste.**

1. *Au site*, les autres points du bloc : la période et son moment ; le
   plancher non majoré ; et ce que la note des révisions a vu en chemin
   (`2026-10-28-etape-4-revisions-au-site.md`, point 2 de « Ce qui reste »).
2. *Au modèle*, s'il le faut : la pension que la présomption
   `pension_d_invalidite_de_la_periode` tire d'une période d'invalidité n'a
   pas de fait qui porte une catégorie, et la saisie demande donc la date avec
   elle ; un fait de la pension présumée la recevrait.
