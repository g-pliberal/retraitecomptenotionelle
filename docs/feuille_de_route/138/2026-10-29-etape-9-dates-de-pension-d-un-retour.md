# Étape 9, suite de la huitième partie : les dates de pension d'un retour

**La demande.** Vague du 28 octobre 2026 : une session par tâche, que le
propriétaire ne suit pas pas à pas, celle-ci seule de la vague sur les pages.
Le point « au site, les dates de pension d'un retour » du bloc « Reprise » de
la huitième partie, que la note « le retour à la CRPCEN et aux IEG dans la
saisie en net » (`2026-10-29-etape-9-retour-dans-la-saisie-en-net.md`,
« Trouvé en chemin ») laissait aux pages : le formulaire propose la date de
chaque pension par `regimesDeBaseSaisis` (`pages.js`), qui lisait les régimes
de chaque métier sous la date du premier recrutement. Au clerc de 2010 à
2014, sans emploi de 2015 à 2024, revenu en 2025, que la carrière sert par la
CRPCEN puis par le régime général, il ne voyait que la CRPCEN, et ne proposait
aucune date.

**Ce que disent les textes.** Rien de neuf à lire : la règle est celle du
modèle, écrite le 25 octobre avec ses sources (loi n° 2023-1250, art. 15, V
et VI ; décrets n° 2025-761 et 2025-799 ; fiche
`maintien_affiliation_crpcen_ieg`). Le formulaire la lit, il ne l'écrit pas.

**Ce qui est fait.**

- *Le test* (`tests/test_web_saisie.py`,
  `test_le_formulaire_date_les_pensions_que_la_carriere_porte`, quatre cas de
  plus), vu rouge sur les trois premiers : le clerc recruté en 2010, sans
  emploi de 2015 à 2024, revenu en 2025, par ses métiers, par une
  interruption déclarée dans son seul métier, par un relevé qui saute ces
  années, date la CRPCEN, puis le régime général ; le formulaire ne proposait
  rien. Le quatrième garde de trop corriger : l'agent des IEG parti fin 2020,
  revenu en 2026, que le maintien couvre, n'a que les IEG, rien à dater.
- *La correction*, dans `regimesDeBaseSaisis` : chaque statut se lit sous la
  date d'entrée que la loi lui donne l'année lue (`Affiliations.dateEntree`,
  sur les retours de la saisie, `Saisie.retours`), à la dernière année de
  chaque métier, ou de ses années sur le relevé, et à la dernière d'avant
  chaque retour qui change cette date. Un retour qui ne la change pas,
  maintenu ou à un statut sans régime fermé, n'ajoute aucune lecture :
  l'artisan revenu à son statut, dont les régimes changent avec les années,
  reste lu à la dernière année de chaque métier, comme avant.

**Ce que montrent les mesures.** Ni les témoins de simulation ni ceux des
pages ne bougent, ni les neuf pages toutes faites (`construire_temoins.py`,
`construire_pages.py`, le 29 octobre, comparés au bit près à ceux d'une
régénération sans le changement) : aucune de leurs saisies ne revient à la
CRPCEN ou aux IEG, et un statut sans retour qui change sa date d'entrée se lit
comme avant. Sur le paquet régénéré, `site` (36 tests, les écrans dans
Chromium compris), `rapide` (3 460) et `test_web_saisie.py` (217) passent. Le
verdict du dépôt, rouge sur 2c322a4, est périmé : la course 1109, sur
0f9f214, est verte, et son verdict n'a pas été commité.

**Ce qui reste**, une session par point : le plafond de 2027 ; au site, la
majoration de la réversion du régime général au non-résident (note « la
limite 5 ante ter (2) », du même jour, « Trouvé en chemin »). Au propriétaire,
sans changement : la CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de
l'article 23, les textes au fac-similé de la note « seuil de février 1991 ».
