# Étape 12, neuvième partie : la nouvelle pension de l'indépendant en cumul, sur son revenu annuel moyen

**Le 19 octobre 2026, la demande.** Deuxième salve de la vague du 19 octobre,
session 13 : le point « la nouvelle pension de l'indépendant, au revenu annuel
(R. 634-1, D. 634-3) » du bloc de l'étape, le 1 de « Ce qui reste » de
`…-points-du-micro-entrepreneur.md`. Avant, l'artisan, le commerçant et le
micro-entrepreneur en cumul intégral avaient le salaire mensuel moyen du
salarié (R. 351-29, III).

**Ce que dit le droit** (journal de veille,
`2026-10-19-action-138-etape-12-nouvelle-pension-de-l-independant.yaml`).

- *De 2023 à 2025.* D. 634-1 applique aux indépendants les règles du régime
  général « à l'exception des articles R. 351-11, R. 351-29, R. 351-29-1 »
  (rédactions du 1er septembre 2023 et du 9 juillet 2024) ; leur revenu annuel
  moyen « correspond aux cotisations versées dans la limite du plafond […]
  permettant la validation d'au moins un trimestre d'assurance […] et versées
  au cours des années civiles de la carrière », et « il est tenu compte du
  revenu annuel de l'année durant laquelle la pension mentionnée à l'article
  L. 161-22-1-1 prend effet » (R. 634-1, sans rédaction après 2025).
- *Depuis 2026.* D. 634-1 n'écarte plus R. 351-29 ; le revenu annuel moyen
  « est déterminé dans les conditions prévues à l'article R. 351-29 », dont
  « 5° Le 2° du C du I n'est pas applicable au calcul de la pension liquidée
  en application de l'article L. 161-22-1 » — l'année d'entrée en jouissance
  reste — et « 7° Les III et IV ne sont pas applicables » (D. 634-3).
- *La caisse.* « le salaire mensuel moyen (travailleurs salariés) ou le revenu
  annuel moyen (travailleurs indépendants) de la période de référence » ;
  « Les salaires de la dernière année sont retenus même si cette année est
  incomplète » (exposé « Retraite personnelle issue d'un cumul emploi
  retraite », modifié le 28 septembre 2026) ; ce revenu est la « Somme des
  revenus et/ou salaires annuels revalorisés des x meilleures années retenues
  ÷ Nombre d'années correspondant » (exposé « Revenu annuel moyen »). Aucune
  instruction ni exemple : « Le dispositif réglementaire n'est pas encore
  entièrement défini », et la « Circulaire Cnav RAM § 5 » que l'exposé cite
  n'a pas de lien.

**Ce qui est fait.**

- *Les deux moteurs* : `_nouvelle_pension` (`nouvellePension`, `seconde.js`)
  prend, pour l'activité du groupe `independants`, la somme des revenus
  revalorisés des années de la période qui valident un trimestre, divisée par
  leur nombre : une année entamée y pèse de ses seuls mois, comme une année
  entière. `NouvellePension` porte le `revenu_annuel_moyen`, que le journal
  de l'échéancier nomme.
- *Tests* : `test_emploi_retraite.py`, le commerçant de février 2023 à
  juillet 2025, posé à la main — ses trois revenus revalorisés, divisés par
  trois, dix fois le salaire mensuel moyen de la salariée au même revenu —,
  et le micro-entrepreneur, sur son revenu annuel moyen ; `moteur.test.js`,
  les mêmes, vus rouges ; le témoin `seconde_pension_commercant_2025`.
- Fiche `seconde_pension` : six rédactions dans la version `loi_2023`, son
  contenu, ses approximations, ses lectures ; deux rédactions de D. 634-1
  prennent un statut, et le cliquet des textes descend d'autant.

**Mesuré.** Aucune pension ne bouge aux six scénarios, sur 887 témoins :
aucun ne met d'indépendant en cumul ; quatre gagnent le champ nul
`revenu_annuel_moyen`. Au même revenu, la nouvelle pension de l'indépendant
vaut de la moitié à la totalité de celle de la salariée : 631 € au lieu de
757 € pour trente mois sur trois années civiles, le témoin nouveau ; 486 € au
lieu de 507 € de février 2023 à janvier 2025, le mois de 2025 ne validant
rien ; 119 € au lieu de 239 € pour six mois de 2023 ; autant quand la période
tombe sur des années civiles entières.

**Trouvé en chemin.**

- D. 634-3, 5°, vise « l'article L. 161-22-1 » ; la nouvelle pension est
  celle de L. 161-22-1-1, que R. 634-1 nommait. Le modèle garde l'année de
  l'effet, comme l'exposé de la Cnav.
- *La même classe, ailleurs.* Depuis 2026, « Le 2° du C du I et le III de
  l'article R. 351-29 du code de la sécurité sociale ne sont pas applicables »
  à l'exploitant agricole (R. 732-60 du code rural) : sa nouvelle pension, que
  le modèle ne calcule pas et que le résultat nomme, ne prendra pas non plus
  le salaire mensuel moyen. Aucun texte lu ne l'écarte des salariés
  agricoles, l'autre régime calculé.
- Le RCI de l'indépendant en cumul intégral : le modèle n'en calcule rien et
  ne le nomme pas, `non_calcules` ne portant que les régimes de base.
- La cotisation minimale de l'artisan et du commerçant, que la note du
  16 octobre (`…-dispenses-de-l-assiette-minimale.md`) dit sans dispense pour
  le pensionné : la nouvelle pension prend le revenu déclaré, sans elle.

**Ce qui reste.**

1. La « Circulaire Cnav RAM » et son § 5, son exemple s'il en a un, quand la
   Cnav la publiera ; la fiche reste `approchee`.
2. À lire : le RCI en cumul intégral, au règlement du RCI ; la cotisation
   minimale de l'indépendant en cumul (D. 633-2), et ses trimestres.
3. Déclarés, légers : la part d'une année dans la période, celle de ses mois
   dans un revenu annuel ; l'arrondi des revenus à l'euro ; plus de
   vingt-cinq années de cumul, pas avant 2048.
4. Les restes du bloc : la veille du projet de loi de financement pour 2027 ;
   au propriétaire, la part de base de l'ordre de D. 133-4 de 2016 à 2019.
