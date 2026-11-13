# Correction de la ligne 1 de la file : l'inapte de la CAVOM de 2016 à 2024

Première ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index du Journal officiel** (à jour du 11 novembre 2026). Statuts de
la CAVOM, article 14, I, 1°, dans la rédaction de l'arrêté du 30 décembre 2015
(JORFARTI000031740853), en vigueur du 1er janvier 2016 au 31 décembre 2024 : la
liquidation « peut intervenir : 1° À partir de 62 ans — En cas d'inaptitude au travail
reconnue dans les conditions prévues aux articles 27 à 33 des statuts de la CNAVPL ; Ou
avec application des coefficients d'anticipation suivants : 0,75 si la retraite est
attribuée lorsque l'affilié est âgé de 62 ans […] ». L'inapte de 62 ans est servi sans
coefficient. L'article 14 récrit au 1er janvier 2025 (arrêté du 12 décembre 2024, annexe,
II, 4°, JORFARTI000050823056) ne le sert plus ainsi : il lui ouvre ses droits à 62 ans
(1°, a), et seuls « les affiliés ayant atteint l'âge de 67 ans » échappent au coefficient
(2°). Le texte tranche ce que la ligne dit.

**Le test d'abord** (`tests/test_sections_juridiques.py`,
`test_la_cavom_sert_l_inapte_sans_coefficient_des_62_ans_de_2016_a_2024` et
`test_l_inapte_de_la_cavom_recoit_un_tiers_de_plus_que_le_valide_de_62_ans`), vu rouge sur
les cinq cas d'inapte de 2016 à 2024. Neuf cas posés à la main, par la requête du
formulaire, servis par le portage et refaits au bit près par le moteur Python
(`servi_et_refait`) : né le 10 mars 1959, à 62 ans le 1er avril 2021, 0,75 valide et 1
inapte ; à 64 ans, 0,85 et 1 ; nés les 10 mars 1957 et 1955, inaptes à 62 ans, 1 ; né le
10 novembre 1962, inapte, la pension le 1er décembre 2024, 1 ; né le 10 décembre 1962,
la pension le 1er janvier 2025, 0,75 ; né le 10 mars 1963, le 1er avril 2025, 0,75.

**L'effet au cas posé** : né le 10 mars 1959, inapte, parti à 62 ans le 1er avril 2021,
13 564,47 € par an avant, 18 085,96 € après, 4 521,49 € de plus (euros de 2026). La note
du 5 novembre écrivait 18 085,97 €, d'une division arrondie.

**La correction.** Un paramètre de période, `age_sans_coefficient_de_l_inapte`
(`regimes/_schema.yaml`, `PeriodeRegime`, le paquet par `_regles_des_sections`) : l'âge
depuis lequel l'affilié dont la carrière déclare l'inaptitude est servi sans coefficient.
`abattementPoints` (`moteur/js/droit/liquider.js`) et son jumeau `abattement_points`
ramènent alors le coefficient à un (`inapteSansCoefficient`, `inapte_sans_coefficient`).
Le régime le porte à 62 aux périodes de 2016 à 2019 et à celle de 2020, coupée en deux :
2020 à 2024, puis 2025, sans lui. La fiche `cavom_ages_minoration` l'écrit dans chaque
version (62 dans celle de 2016, nul ailleurs), et
`test_chaque_pension_minoree_porte_les_ages_et_le_taux_de_sa_version` le vérifie chaque
premier du mois. Dans la fiche, l'erreur n'est plus déclarée : elle est racontée au champ
`effet`.

**Ce que la correction déplace.** Aucun témoin de simulation. Le catalogue compte une
période de plus qui annonce la réversion, 961 au lieu de 960 : la page des droits non
cotisés le dit, refaite. Le cliquet des rédactions sans statut baisse de 9229 à 9228 : la
fiche cite L. 643-4 dans sa rédaction de 2008 (LEGIARTI000019959512) et L. 643-5
(LEGIARTI000006743795), relus.

**Ce que la correction laisse, déclaré dans la fiche.**

- Seule compte l'inaptitude que la carrière déclare : les articles 27 à 33 des statuts de
  la CNAVPL ne sont pas lus, et l'invalide ou le titulaire d'une incapacité permanente
  n'est pas réputé inapte ici.
- L'inapte né avant 1959, entre l'âge d'ouverture de sa génération et 62 ans, garde le
  coefficient : le texte ne tranche pas (déjà déclaré).
- Avant 2016, où les statuts ne sont pas lus, l'inapte garde le coefficient.
- La base de l'inapte libéral garde son coefficient à 62 ans (0,7625 au cas posé), écart
  déjà déclaré ailleurs, hors de cette ligne.

**La classe, pour les lignes suivantes.** Le paramètre sert tel quel à une autre section
qui écrit un âge de l'inapte sans coefficient : la CARCDSF (ligne 23 de la file) ; la
CAVEC, la CARPV et la CAVAMAC, que la fiche de la CAVOM rangeait dans la même classe et
que la file ne nomme pas pour l'inapte. Chacune demande son texte relu : rien n'y est
touché ici.

**Vérifié** : `python -m pytest -m rapide`, `-m site`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, `test_invalidite.py`, verts.
