# L'âge où s'ouvre la base des libéraux, et leurs sections à leur âge

File L de la vague 6, les 3 et 4 novembre 2026 : l'écart (c) de la relecture R-E-bis
(note `2026-11-03-relecture-corrections-r-e.md`) — le vétérinaire, l'expert-comptable et
le biologiste libéral servis de leur base à 60 ans. Textes lus pendant la session dans
les index LEGI et JORF du dépôt, mis à jour de l'incrément `20261103-214151`.

## Ce que disent les textes

- **La base.** « La liquidation de la pension prévue à l'article L. 643-1 peut être
  demandée à partir de l'âge prévu au premier alinéa de l'article L. 351-1 » (L. 643-3,
  I : LEGIARTI000006743789 en 2004, LEGIARTI000047453031 en 2023, même phrase), l'âge de
  L. 161-17-2 : « soixante-deux ans pour les assurés nés à compter du 1er janvier 1955 »
  (LEGIARTI000025014605, pensions jusqu'au 31 août 2023) ; D. 161-2-1-9
  (LEGIARTI000047634502, pensions du 1er septembre 2023) : « 6° Soixante-deux ans pour
  les assurés nés entre le 1er janvier 1955 et le 31 août 1961 inclus ; 7° Soixante-deux
  ans et trois mois pour les assurés nés entre le 1er septembre 1961 et le 31 décembre
  1961 inclus » ; L. 161-17-2 (LEGIARTI000053280889, pensions du 1er septembre 2026) :
  « 3° Soixante-deux ans et neuf mois, pour les assurés nés entre le 1 er janvier 1963 et
  le 31 mars 1965 » … « 7° Soixante-trois ans et neuf mois, pour les assurés nés en
  1968 ». Ni L. 643-3 ni L. 644-1 (LEGIARTI000037063798) ne lient la complémentaire à
  la base.
- **La CARPV.** « Pour bénéficier de la retraite complémentaire, les assujettis doivent
  avoir versé les cotisations exigibles de l'ensemble des régimes appelés par la CARPV »
  (article 33) ; « les adhérents remplissant les conditions de l'article 33 peuvent
  demander à bénéficier de leur pension de retraite complémentaire dès leur soixantième
  anniversaire » (article 34) : statuts de 2021 (JORFARTI000044220745), règlement de 2026,
  articles 1er et 2 (JORFARTI000054436031), mot pour mot. La base n'est une condition
  que de la retraite progressive (« qu'il liquide ou qu'il ait déjà liquidé sa pension de
  retraite de base des libéraux », article 52 ; règlement, article 11).
- **La CAVEC.** « La retraite est liquidée sur demande […] - à 65 ans à taux plein ; -
  entre 60 et 65 ans, avec application d'un abattement définitif de 1,25 % par trimestre
  manquant » : statuts de 2008, article 3.13 (JORFARTI000018197778) ; de 2018, partie 2,
  article 12 (JORFARTI000037363871) ; règlement de 2026, article 1.1.3
  (JORFARTI000054435943). La base n'y conditionne que l'inapte de 2008 à 2019.
- **Les biologistes directeurs de laboratoire.** Le décret n° 81-1046 renvoie l'âge au
  règlement de la section (article 2). Statuts de la CAVP, article 14 (arrêté du 23 juin
  2011, JORFARTI000024270214, publié le 29 juin, sans date d'effet : le 30 juin 2011) :
  « Le biologiste remplissant les conditions pour prétendre au versement de la
  prestation supplémentaire de vieillesse peut demander à en bénéficier à partir de
  l'âge fixé à l'article L. 161-17-2 du code de la sécurité sociale » ; règlement de
  2026, article 1er (JORFARTI000054436087) : « à partir de l'âge fixé à l'article
  L. 161-17-2 ». La fiche du régime disait 60 ans, d'après le guide de la CNAVPL.
- **La base d'avant 2004.** « L'entrée en jouissance de l'allocation […] sans pouvoir
  être antérieure au soixante-cinquième anniversaire » (R. 643-6, LEGIARTI000006751828) ;
  « Les assurés peuvent recevoir à partir de l'âge de soixante ans […] une allocation de
  vieillesse […] affectée des coefficients d'anticipation […] 0,75 […] soixante ans ;
  […] 0,95 […] soixante-quatre ans » (R. 643-7, LEGIARTI000006751830), « sous réserve de
  la cessation de l'activité professionnelle libérale » (L. 643-5, LEGIARTI000006743793),
  du 21 décembre 1985 au 31 décembre 2003. La fiche du régime disait 65 ans, sans
  anticipation : l'erreur que masquait la première, et que la corriger seule aurait
  changée en refus.

## Ce qui change, dans les deux moteurs

1. `ouvrir` (`ouvrir.py`, `ouvrir.js`) : parmi les régimes en points, la base décide
   (`bases_d_abord`, `basesDAbord`) ; une complémentaire ne répond que si aucune base
   n'est là. `sans_ages_propres` (la date des cas types, l'âge du taux plein, la fin de
   l'indemnisation, l'ouverture d'une unité) suit la même règle.
2. `departs` : la CARPV et la CAVEC forment une unité chacune (`SANS_LEUR_BASE`) ; leur
   date les sépare de la base quand elles s'ouvrent avant elle.
3. Données : l'ASV des directeurs de laboratoire s'ouvre à la génération depuis la
   période de 2009 (avant le 30 juin 2011, seuls les nés avant le 1er juillet 1951
   pouvaient liquider, à qui la table rend 60 ans) ; la base d'avant 2004 s'ouvre à 60
   ans, minorée de 1,25 % par trimestre que la durée n'annule pas (fiche neuve
   `cnavpl_allocation_avant_2004`).

## Les valeurs attendues, à la main

Une pension prend effet le premier jour du mois qui suit l'anniversaire de l'âge.

| Naissance | 60 ans | Âge légal | Date de la base |
|---|---|---|---|
| 10 février 1955 | 1er mars 2015 | 62 ans (2011) : 10 février 2017 | 1er mars 2017 |
| 10 février 1961 | 1er mars 2021 | 62 ans, pension avant le 1er septembre 2023 | 1er mars 2023 |
| 10 octobre 1961 | 1er novembre 2021 | 62 a 3 m (D. 161-2-1-9, 7°) : 10 janvier 2024 | 1er février 2024 |
| 10 février 1964 | 1er mars 2024 | 62 a 9 m (2026, 3°) : 10 novembre 2026, après le 1er septembre 2026 | 1er décembre 2026 |
| 10 février 1968 | 1er mars 2028 | 63 a 9 m (2026, 7°) : 10 novembre 2031 | 1er décembre 2031 |

À 60 ans, la CARPV et la CAVEC : 65 − 60 = 5 ans = 20 trimestres × 1,25 % = 25 %,
coefficient 0,75. Avant 2004, né le 10 février 1930 : 0,75 au 1er mars 1990, 0,80 en
1991, 0,85, 0,90, 0,95 en 1994, 1 en 1995 ; non ouvert à 59 ans.

Le vétérinaire né le 10 février 1964 parti à 60 ans (requête du simulateur, début à 26
ans, deux salaires moyens) : avant, la CARPV 15 158,05 € et la CNAVPL 7 480,70 € dès
mars 2024 ; après, la CARPV 15 158,05 € dès mars 2024, la CNAVPL 7 886,55 € dès
décembre 2026. Le biologiste du même âge : non ouvert à 60 ans, comme le libéral de la
Cipav.

## Tests, témoins, coût

`tests/test_ouverture_des_liberaux.py` (35 cas, vus rouges puis verts, par
`servi_et_refait` : portage et moteur Python) ; `-m rapide` : rouges les seules pages
toutes faites (`test_pages_en_dossier`) ; le cliquet des textes descend à 9 344 ; la
déclaration `("cnavpl", "age")` de `test_regle_de_chacun.py` se retire, l'âge ne
basculant plus en 2004. Témoins (`construire_temoins.py`) : 42 bougent ; 28 libéraux nés
en 1925 et 1935, partis à 64 ans, baissent de 1,48 à 4,64 % au scénario 1 (l'allocation
au coefficient 0,95) ; 12 vétérinaires, experts-comptables et biologistes de 1955 à
1968 n'ont que l'âge opposé qui passe de 60 ans à l'âge légal ; `bascule_1980` et
`bascule_2000`, l'origine de l'âge du régime fusionné (la CNBF au lieu de la CNAVPL, au
même âge). Le coût, refait par GitHub : les cas types de ces trois statuts partent à
l'âge légal et non plus à 60 ans, et l'allocation d'avant 2004 est minorée.

## Ce que l'étape laisse

- **La CRPNPAC** (complémentaire en annuités, ouverte à 50 ans) ouvre encore le régime
  général du personnel navigant : né en 1964, parti à 55 ans, il le touche. Même classe,
  à instruire au code de l'aviation civile.
- Présumées suivre leur base sans lecture de leurs statuts : la CAVOM, la CARPIMKO, la
  CAVP, la CARCDSF, la CPRN (âges propres), et les complémentaires des salariés, comme
  avant.
- L'ASV des directeurs : le coefficient court jusqu'à 67 ans à toute génération, quand
  les textes disent l'âge de L. 351-8, 1°, 65 ans aux nés avant juillet 1951.
- R. 643-7 compte l'âge en années révolues, le modèle par trimestre (fiche, déclaré) ;
  l'inapte et l'ancien prisonnier d'avant 2004 ; avant 1985, rien n'est lu.
- Le bloc « Reprise » de l'action 130, que la file E récrit, devrait dire : « La base des
  libéraux s'ouvre à l'âge légal, la CARPV et la CAVEC à 60 ans à part, l'allocation
  d'avant 2004 dès 60 ans minorée (`130/2026-11-04-ouverture-de-la-base-des-liberaux.md`) ;
  reste la CRPNPAC, qui ouvre le régime général du personnel navigant à 50 ans. »

Renvoi du 5 novembre 2026 : le cliquet des textes descend à 9 334, non à 9 344 ;
voir `2026-11-05-corrections-de-la-relecture-r-l.md`.
