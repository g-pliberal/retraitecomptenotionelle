# Correction de la ligne 3 de la file : la CPRN ouverte le 1er janvier 2024 au notaire parti avant

Troisième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index du Journal officiel** (à jour du 11 novembre 2026). Arrêté du
29 novembre 2023, annexe, I, 3° (JORFARTI000048679350), mot pour mot : « L'article 18 est
remplacé par les dispositions suivantes : " Art. 18. - […] L'âge de l'ouverture du droit à
pension de retraite est celui mentionné à l'article L. 161-17-2 du code de la sécurité
sociale. " » ; article 2 (JORFARTI000048679346) : « Les dispositions du présent arrêté
entrent en vigueur le 1er janvier 2024. » L'annexe, lue en entier, ne porte aucune
disposition transitoire. Statuts de 2017, article 19 (JORFARTI000034975971), que l'arrêté
de 2023 ne touche pas : « Le droit à l'allocation est fixé au premier jour du mois civil
qui suit la date de fin d'exercice ou la date souhaitée par l'affilié ». L. 161-17-2 en
vigueur le 1er janvier 2024 (LEGIARTI000047452768) et D. 161-2-1-9, 6°
(LEGIARTI000047634502) : « Soixante-deux ans pour les assurés nés entre le 1er janvier
1955 et le 31 août 1961 inclus ». Le texte tranche ce que la ligne dit.

**Le test d'abord** (`tests/test_sections_juridiques.py`, deux cas de plus à
`CPRN_AU_TEXTE`, que joue
`test_la_cprn_sert_ses_ages_et_ses_coefficients_dans_les_deux_moteurs`), vu rouge sur le
coefficient 0,85 et la pension « servie à partir du 1er avril 2025 ». Deux cas posés à la
main, par la requête du formulaire, servis par le portage et refaits au bit près par le
moteur Python (`servi_et_refait`) : né le 10 mars 1961, parti à 62 ans le 1er avril 2023,
la CPRN le 1er janvier 2024, à 62 ans, 9 mois et 22 jours, 4 ans, 2 mois et 9 jours avant
67 ans, 17 trimestres compté le trimestre entamé, 0,7875 ; né le 10 mars 1960, parti à
62 ans le 1er avril 2022, le 1er janvier 2024, 13 trimestres, 0,8375.

**L'effet au cas posé** : né le 10 mars 1961. Avant, la CPRN le 1er avril 2025, à 64 ans,
0,85, 14 679,08 € par an de 2025 ; après, le 1er janvier 2024, 0,7875, 13 164,74 € par an
de 2024. Quinze mois de pension de plus : 13 164,74 × 15 / 12 = 16 455,93 € aux valeurs
de 2024, 16 999,67 € à celles de 2025 que la file retenait (14 679,08 / 0,85 × 0,7875 ×
15 / 12) ; puis une pension plus basse de 1 079,34 € par an, aux valeurs de 2025. Né en
mars 1960 : trois mois de plus, 13 943,26 € par an de 2024, 0,8375 au lieu de 0,85.

**La correction.** `ouvertureDe` (`moteur/js/droit/departs.js`) et son jumeau `_ouverture`
lisaient l'âge où s'ouvre une unité dans les règles en vigueur au départ déclaré. Quand
ces règles ne l'ouvrent pas encore, ils relisent désormais celles de chaque mois qui
suit, jusqu'au premier où l'assuré a l'âge qu'elles lui opposent : la pension prend effet
sous la rédaction de sa date d'effet. Deux fonctions en sortent, `periodesDeLUnite` et
`ouvertureSous`. Rien ne change quand les règles ouvrent déjà au départ déclaré, ni quand
elles ne changent pas d'ici l'ouverture.

**La classe.** La correction vaut pour toute unité, de tout régime, dans les deux sens :
une règle qui avance l'âge ouvre le jour de son entrée en vigueur, une règle qui le recule
reporte l'ouverture. Sur les 933 témoins de simulation, un seul bouge
(`cumul_notaire_cprn_2022`, −0,64 % aux scénarios 1, 3 et 5) ; aucune page.

**Ce que la correction laisse, déclaré dans la fiche `cprn_ages_decote_enfants`.**

- Le modèle sert la CPRN dès son ouverture ; l'article 19 laisse l'affilié choisir une
  date plus tardive, qu'il dit par la date de sa demande.
- Le notaire qui exerce encore, en cumul, le jour où les statuts ouvrent sa pension est
  liquidé ce jour-là, avant la fin de son exercice : le témoin `cumul_notaire_cprn_2022`,
  né en janvier 1960, exerçant jusqu'à la fin de janvier 2024, passe du 1er février 2024
  (0,85, 6 395,58 € par an) au 1er janvier (0,8375, 6 301,53 €, janvier non servi), 94,05 €
  par an de moins que ce que l'article 19 lui donne. À reprendre avec le cumul des
  sections, hors de cette ligne.
- Le trimestre entamé, que le texte ne tranche pas (16 trimestres, 0,80, sans lui).
- La carrière longue et le départ des assurés handicapés se lisent toujours acquis au
  départ déclaré.

**Les fiches.** `cprn_ages_decote_enfants` : l'erreur n'est plus déclarée, elle est
racontée au champ `effet` ; relue ce jour. `liquidation_regime_par_regime` : l'écart
retiré, la correction à l'historique.

**Vérifié** : `python -m pytest -m rapide` (5 001 verts), les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, `test_sections_juridiques.py`,
`test_sections_liberales.py`, `test_sections_sante.py`, `test_ouverture_des_liberaux.py`,
`test_ouverture_des_navigants.py`, `test_complementaires_liberales_a_leur_age.py`,
`test_departs.py`, `test_departs_generations.py`, `test_cumul_activites.py`,
`test_carte.py`, verts. `regenerer.py --verifier` : seuls trois chiffres ancrés de la
prose sont périmés, que GitHub refait.
