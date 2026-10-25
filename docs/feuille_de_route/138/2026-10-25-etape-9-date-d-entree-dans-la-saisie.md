# Étape 9, suite de la huitième partie : la date d'entrée dans la saisie en net

**La demande.** Dixième vague, le 25 octobre 2026 : une session par tâche,
que le propriétaire ne suit pas pas à pas, celle-ci seule du lot sur les
pages. Le point « la date d'entrée dans la saisie en net (pages) » du bloc
« Reprise » de la huitième partie, que la note « date d'entrée dans la fiche
de paie » (`2026-10-18-etape-9-date-d-entree-dans-la-fiche-de-paie.md`,
« Pour la session des pages ») laissait aux pages : la fiche lit les régimes
de la date d'entrée dans le statut, mais la saisie en net remontait au brut
par celle d'un nouvel entrant. Un champ de plus s'il le fallait, sa forme au
propriétaire.

**Ce que disent les textes.** Rien de neuf à lire : les clauses du
grand-père sont dans `affiliations.yaml`, avec leurs textes (note du
18 octobre). Une seule n'y ferme pas le statut : le libéral non réglementé
installé avant le 1er janvier 2019 « reste affilié » à la CNAVPL et à la
Cipav (loi n° 2017-1836, art. 15) ; installé depuis, il relève du régime
général et du RCI (L. 640-1, rédaction du 1er janvier 2018), et le
formulaire le propose à toute date.

**Ce qui est fait.**

- *Pas de champ de plus.* Le début de chaque métier date déjà l'entrée dans
  son statut, et la carrière la lit ainsi : l'ouverture de la première
  période de chaque affiliation (`lignesDuParcours`), ou janvier de la
  première année d'un relevé (`Carriere.dateEntree`). La saisie la donne de
  même, `Saisie.dateEntree(affiliation)` ; `null` hors de la carrière, ou
  tant que le relevé ne se lit pas. `affiliationDe`, tiré d'`abattu`, route
  la ligne du micro-entrepreneur de la Cipav vers le libéral, comme
  `parcours`.
- *L'échelle la passe à la fiche* (`Contexte.echelle`), à
  `salaireBrutDepuisNet` et à `salaireNetDepuisBrut`, comme la part de
  primes : tout ce qui convertit la reçoit — le revenu de chaque métier et
  de l'activité après le départ, la bascule net/brut, les repères du champ
  (le SMIC et le salaire moyen nets), le revenu déduit d'une pension,
  l'avertissement des statuts sans fiche.
- *Les tests* (`tests/test_web_saisie.py`, six tests, neuf cas) : l'agent de
  la SNCF entré en 1996 qui saisit 2 653,99 € nets par mois en 2026 a
  3 333,33 € bruts, posés à la main (3 352,62 € avant) ; de même entré en
  2015 après le privé, et son activité après le départ, sur ses métiers ou
  sur un relevé ; le libéral non réglementé installé en décembre 2018
  remonte comme la profession libérale réglementée, installé en janvier 2019
  comme le commerçant ; la date de la saisie est celle de la carrière, sur
  quatre saisies, dont celle du micro-entrepreneur de la Cipav ; la page :
  2 654 € nets font un lien vers 3 333 € bruts, qui revient à 2 654 €, et les
  repères sont les nets de la fiche de l'agent ; un relevé illisible se
  refuse en net, au lieu de faire tomber la page.

**Ce que montrent les mesures** (2 500 € nets par mois saisis en 2026, le
brut que la saisie en tire) : avant, 3 158,09 € pour chaque agent d'un
régime fermé, la fiche d'un nouvel entrant, salarié du privé ; après,
3 139,92 € pour l'agent de la SNCF entré en 1992, 3 197,76 € pour ceux de
la RATP et des IEG entrés en 1997, 3 228,32 € pour le clerc de notaire,
3 149,81 € pour l'agent de la Banque de France, 3 033,25 € pour le mineur
entré en 1995. Le libéral non réglementé installé en 2005, de 4 349,23 € à
4 099,52 €. Le membre du CESE n'a pas de fiche : ses 2 500 € se lisent tels
quels, avant comme après. Ni les témoins de simulation ni ceux des pages ne
bougent (`construire_temoins.py`, le 25 octobre).

**Trouvé en chemin.** Le formulaire propose la date de chaque pension par
`regimesDeBaseSaisis` (`pages.js`), qui date chaque métier de son propre
début, et lit les régimes du micro-entrepreneur de la Cipav sous son statut,
non sous celui du libéral : à la carrière d'un micro-entrepreneur de la
Cipav de 2009 à 2014, puis salarié, il propose le régime général et le RSI,
quand elle porte la CNAVPL. `Saisie.dateEntree` et `affiliationDe` le
diraient comme la carrière ; à une session des pages, avec son test.

**Ce qui reste**, une session par point : le plafond de 2027 ; aux pages,
les dates de pension du formulaire (« Trouvé en chemin ») ; la limite 5 ante
ter (2), en fin d'étape ; au propriétaire, la CAMIEG, l'écrêtement du
minimum de la SNCF, l'ASPA de l'article 23, et les textes au fac-similé de
la note « seuil de février 1991 ».
