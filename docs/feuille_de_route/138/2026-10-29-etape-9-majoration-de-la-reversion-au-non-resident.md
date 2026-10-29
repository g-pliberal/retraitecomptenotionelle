# Étape 9, suite de la huitième partie : les majorations pour enfants de la réversion du régime général, hors de la cotisation du non-résident

**La demande.** Vague du 28 octobre 2026 : une session par tâche, que le
propriétaire ne suit pas pas à pas, celle-ci seule de la vague sur les pages.
Le point « au site, la majoration de la réversion au non-résident » du bloc
« Reprise » de la huitième partie, que la note « la limite 5 ante ter (2) »
(`2026-10-29-etape-9-limite-5-ante-ter.md`, « Trouvé en chemin ») rendait aux
pages, après la note « réversion de la SNCF » du 18 octobre : `reverse`
(`pages.js`) n'ôtait de l'assiette de la cotisation maladie que la majoration
du défunt (`ligne.majoration`), nulle au régime général, dont la ligne porte
dans son montant la majoration pour trois enfants du survivant
(`majoration_trois_enfants`) ; aucun test ne tenait le cas.

**Ce que disent les textes, relus le jour même dans l'index LEGI, à jour au
25 octobre.** Rien de neuf : L. 131-2, 1° (LEGIARTI000047453476), que l'étape
cite depuis le 4 octobre, soumet à la cotisation les avantages de retraite du
régime général « à l'exclusion des bonifications ou majorations pour enfants
autres que les annuités supplémentaires ». La réversion « est majorée lorsque
le bénéficiaire remplit les conditions fixées à l'article L. 351-12 » (L. 353-1,
LEGIARTI000047453693), de 10 % (R. 353-2, LEGIARTI000006749405), et son
titulaire a droit à « une majoration forfaitaire de sa pension de réversion
pour chaque enfant dont il a la charge » (L. 353-5, fiche
`majoration_forfaitaire_reversion`). Deux majorations pour enfants, donc, que
la cotisation du non-résident sur la base du régime général (L. 131-9 ;
D. 242-8 ; fiche `cotisation_maladie_des_non_residents`) ne frappe pas. La
seconde avait le défaut de la première, dans la même ligne du code : la
session règle les deux.

**Ce qui est fait.**

- *Le test* (`tests/test_web.py`,
  `test_le_non_resident_ne_paie_rien_sur_les_majorations_pour_enfants_de_la_reversion`),
  vu rouge sur ses deux cas : le salarié du privé parti à soixante-deux ans,
  père de trois enfants, qui réside en Espagne sans pension espagnole, la
  France le soignant ; son décès supposé cette année, puis en juin 2035, quand
  sa conjointe a cinquante-cinq ans et son dernier enfant douze. Chaque ligne
  de la carte de la réversion, chaque majoration et le total, contre le calcul
  posé à la main : 3,20 % de la base du régime général et 4,20 % des
  complémentaires, hors des majorations pour enfants.
- *La correction*, dans `reversionDuConjoint` : `reverse` ôte de l'assiette
  toutes les majorations pour enfants de la ligne (`majorationsPourEnfants`),
  celle du défunt, celle de trois enfants et celle d'enfant à charge ; chacune,
  dite à part, ne paie aucune cotisation maladie (`pourEnfants`), ni ce que
  devient celle d'enfant à charge quand un enfant cesse de l'être.
- *La limite 5 ante ter (2)* : sa phrase récrite, avec ce qui reste.

**Ce que montrent les mesures.** Au premier cas, la réversion du régime général
passe de 978 € à 980 € par mois, dont 92 € de majoration pour trois enfants au
lieu de 89 € ; au second, de 1 087 € à 1 094 €, dont 92 € et 114 € de majoration
pour enfant à charge au lieu de 110 €. Le résident ne bouge pas : la base du
régime général ne lui prend aucune cotisation maladie. Ni les témoins de
simulation ni ceux des pages ne bougent, ni les neuf pages toutes faites
(`construire_temoins.py`, `construire_pages.py`) : aucune de leurs saisies ne
réside hors de France avec une réversion majorée. `site` (36 tests, les écrans
dans Chromium compris), `rapide` (3 465) et les fichiers de la zone,
`test_web.py`, `test_web_saisie.py` et `test_net_pensions.py` (580), passent.

**Ce qui reste.** Ce qu'une révision sous le plafond de ressources, ou la
limite de cumul d'avant juillet 2004, retire à la réversion du régime général,
la carte le nette encore au taux de la ligne, la part de la majoration pour
trois enfants comprise : la ligne n'en porte que la somme (`revisions`,
`reduction_du_cumul`), et seul le modèle, dans ses deux langues, pourrait l'en
séparer. L'écart, 3,20 % de cette part, reste sous l'euro par mois tant que la
réduction ne passe pas trois cents euros ; la limite le dit. À l'étape : le
plafond de 2027, au 1er janvier (note du 28 octobre) ; les fiches, à sa fin,
dont `cotisation_maladie_des_non_residents`, qui ne nomme pas encore
`reversionDuConjoint` parmi son code. Au propriétaire, sans changement : la
CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de l'article 23, les textes
au fac-similé.
