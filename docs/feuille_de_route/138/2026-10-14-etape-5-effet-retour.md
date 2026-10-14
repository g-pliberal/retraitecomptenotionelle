# Étape 5, quatrième partie : l'effet retour de la page Coût, au modèle

**La demande.** En tête du rang lourd du classement
(`2026-10-09-classement-par-poids.md`) : l'ASPA que déclenchent les petites
pensions des scénarios 2 à 5, et les impôts affectés, que `cout.py` tenait
fixes. L'IPP (Perspectives budgétaires 2027, juin 2026) chiffre le gain public
« inférieur d'environ 20 % à 25 % » à l'économie des régimes ; le simulateur
de S. Aurain le fait aussi (registre, `simulateur_aurain`, 138.5). Le point
attendait l'action 147, que le propriétaire a close le 14 octobre sur l'écart
déclaré à l'horizon.

**Ce qui est fait.** `src/retraite_notionnelle/effet_retour.py`, branché sur
la trajectoire (`cout._avenir`) :

- La méthode est celle de la garantie du scénario 6 : la distribution des
  pensions de droit direct de l'EIR de 2020, que `_garantie_distribution`
  cale, déplacée par la pension moyenne de la grille de chaque système. Sa
  tranche ouverte (4 500 € et plus), que la garantie laisse à sa borne, reçoit
  la valeur qui redonne la moyenne publiée, majorations comprises (1 476 €).
- L'ASPA : le plafond de l'année, personne seule et moitié du couple, mêlés
  comme la garantie mêle ses planchers (recensement de 2021), au même taux de
  recours (un sur deux), sur la part des retraités qui a 65 ans.
- Les prélèvements d'une personne seule de 70 ans qui n'a que sa pension :
  la tranche de CSG de son revenu fiscal présumé, la CRDS et la CASA qu'elle
  prélève, au barème de 2026 ramené sur les prix ; l'impôt sur le revenu de
  l'année, sur la pension nette de la CSG déductible, au barème lu puis
  projeté sur les prix (`impot_revenu.py`).
- Ce qui sort, chaque année depuis 2019 et pour chaque scénario 2 à 5, sont
  deux TAUX rapportés à ce que la distribution perd en masse
  (`EffetRetourAnnuel.aspa`, `.prelevements`), appliqués à l'économie des
  régimes de la page, celle de la dépense du COR : la distribution de l'EIR et
  la dépense publiée ne sont pas à la même échelle, un taux se transporte.
  `AvenirAnnuel.economie_constants`, `effet_retour_constants`,
  `gain_public_constants` ; `Avenir.part_effet_retour(scenario, debut, fin)`.
- Le scénario 6 n'en a pas : sa garantie remplace l'ASPA et se chiffre à part.

**Ce que cela donne**, sous la référence. De 2026 à 2070, l'effet retour
reprend 26,8 % de l'économie du scénario 2, 27,5 % du 3, 27,7 % du 4 et
28,3 % du 5 : un peu plus que l'IPP, et c'est l'ASPA qui fait l'écart des
scénarios. En 2050, l'ASPA reprend 8,9 % de l'économie du scénario 2, dont
les pensions tombent au tiers, et 3 à 4 % des autres ; les prélèvements, 18 à
25 %. Le solde de la page ne bouge pas : l'effet retour est à côté, et aucun
témoin ni chiffre ancré ne le porte encore. `tests/test_effet_retour.py`
(niveau complet) tient l'ordre de grandeur, entre 15 et 35 %.

**Limites**, à reporter dans `docs/limites/5-bis-cout-agrege.md` à la fin de
l'étape : le déplacement uniforme de la distribution sous-estime l'ASPA d'un
scénario sans minimum contributif ; ni quotient conjugal, ni revenus du
patrimoine, ni cotisation maladie des complémentaires ; le barème de CSG de
2026 pour toutes les années ; rien avant 2019, faute de barème.

**Ce qui reste**, dans l'ordre :

1. *Au propriétaire* : l'effet retour entre-t-il dans le solde et la dette de
   la page, ou reste-t-il à côté, en ligne « gain public » ? Le modèle le
   tient à côté ; l'entrer déplace tous les soldes des scénarios 2 à 5.
2. *L'affichage*, à la session du site : une ligne « gain public » dans la
   page Coût, et sa part de l'économie face à l'IPP ; il passe par la table
   du paquet (`construire_donnees.py`, `agregats.json`, `agregats.js`).
3. *L'ASPA d'un scénario sans minimum contributif*, déformée et non déplacée :
   la part des retraités au minimum (EACR, `caracteristiques`) le permet.
4. Les années d'avant 2019, au barème de CSG de chacune.
5. Puis le reste de l'étape : l'impôt au site, le bénéfice des indépendants,
   les règles d'avant 1981.
