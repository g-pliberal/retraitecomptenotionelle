# Correction de la ligne 2 de la file : l'inapte de la CAVOM ouvert à 62 ans depuis 2025

Deuxième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index du Journal officiel** (à jour du 11 novembre 2026). Statuts de
la CAVOM, article 14, dans la rédaction de l'arrêté du 12 décembre 2024 (annexe, II, 4°,
JORFARTI000050823056), en vigueur le 1er janvier 2025, et règlement de 2026 (arrêté du
10 juillet 2026, annexe I, article 1er, I, JORFARTI000054435969), mot pour mot : « 1° L'âge
d'ouverture des droits à pensions est fixé à : a) 62 ans pour les affiliés relevant du a
du 2° de l'article L. 643-4 du code de la sécurité sociale ; b) 64 ans à compter de la
génération 1968. Pour les affiliés nés avant le 1er janvier 1968, cet âge est fixé à :
[…] - 62 ans et 6 mois ans pour les affiliés nés en 1965 ; - 63 ans pour les affiliés nés
en 1966 ; - 63 ans et 6 mois pour les affiliés nés en 1967 ». L. 643-4, 2°, a
(LEGIARTI000047453026, en vigueur depuis le 1er septembre 2023) : « Reconnus inaptes au
travail dans les conditions prévues à l'article L. 643-5 ». Le 2° ne sert sans
coefficient que « les affiliés ayant atteint l'âge de 67 ans », et le 3° fixe « 5 % par
année manquante » : l'inapte part à 62 ans avec 0,75. Le texte tranche ce que la ligne dit.

**Le test d'abord** (`tests/test_sections_juridiques.py`,
`test_la_cavom_ouvre_l_inapte_a_62_ans_depuis_2025` et
`test_l_inapte_de_la_cavom_ne_en_1965_gagne_six_mois_de_pension`), vu rouge sur les quatre
inaptes (`non_ouverte`). Six cas posés à la main, par la requête du formulaire, servis par
le portage et refaits au bit près par le moteur Python (`servi_et_refait`) : nés les
10 mars 1965, 1966, 1967 et 1968, inaptes, partis à 62 ans, la complémentaire le 1er avril
2027, 2028, 2029 et 2030, coefficient 0,75, la base plus tard ; nés les 10 mars 1965 et
1968, valides, à 62 ans : rien ne s'ouvre.

**L'effet au cas posé** : né le 10 mars 1965, inapte, 62 ans le 10 mars 2027. Avant, le
modèle refusait le départ à 62 ans et servait la complémentaire le 1er octobre 2027, à
62 ans et 6 mois ; après, il la sert le 1er avril 2027 : six mois de pension, 16 635,98 /
2 = 8 317,99 € (euros de 2026). Né en 1968, deux ans de pension (essai : 17 870,58 € par
an, servis le 1er avril 2030 au lieu du 1er avril 2032).

**La correction.** Un paramètre de période, `age_ouverture_de_l_inapte`
(`regimes/_schema.yaml`, `PeriodeRegime`, le paquet par `_regles_des_sections`) : l'âge
auquel la section ouvre ses droits à l'affilié dont la carrière déclare l'inaptitude,
quand sa génération ouvre plus tard. `ageOuverture` (`moteur/js/droit/ouvrir.js`) et son
jumeau `age_ouverture` l'opposent à l'âge de la table. Le régime le porte à 62 à sa
période de 2025. La CAVOM se demandant à son âge, sans la base, l'inapte reçoit sa
complémentaire au départ demandé et sa base à l'âge de sa génération. La fiche
`cavom_ages_minoration` l'écrit dans chaque version (62 dans celles de 2025 et de 2026,
nul avant), et `test_chaque_pension_minoree_porte_les_ages_et_le_taux_de_sa_version` le
vérifie chaque premier du mois. Dans la fiche, l'erreur n'est plus déclarée : elle est
racontée au champ `effet`.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page ; le paquet
porte le paramètre de plus. `regenerer.py --verifier` : tout est à jour.

**Ce que la correction laisse, déclaré dans la fiche.**

- Seule compte l'inaptitude que la carrière déclare : L. 643-5 n'est pas opposé, et
  l'invalide ou le titulaire d'une incapacité permanente n'est pas réputé inapte ici.
- La base du même inapte ne s'ouvre pas à 62 ans (écart déclaré à
  `liquidation_regime_par_regime`) : sa complémentaire part seule.
- Entre 62 ans et l'âge de sa génération, un âge non entier laisse des années manquantes
  non entières (né en 1965, à 62 ans et 3 mois : le modèle sert 0,75) : le texte, « non
  susceptible de fractionnement », ne dit pas l'arrondi (déjà déclaré).
- La date d'effet au trimestre civil, ligne 12 de la file.

**La classe, pour les lignes suivantes.** Le paramètre sert tel quel à une autre section
qui écrit un âge d'ouverture de l'inapte ; l'inapte de la CARCDSF né en 1965, refusé à
62 ans, tient à sa base, que la CARCDSF suit : rien n'y est touché ici.

**Vérifié** : `python -m pytest -m rapide`, `-m site`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, `test_invalidite.py`,
`test_sections_liberales.py`, `test_carte.py`, verts.
