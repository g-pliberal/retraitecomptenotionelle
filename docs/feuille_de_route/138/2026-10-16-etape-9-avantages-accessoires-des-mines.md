# Étape 9, suite de la huitième partie : les avantages accessoires des mines, dans l'assiette de leur cotisation maladie

**La demande.** Vague quater du 16 octobre 2026, session 8 sur 12 : le
point 3 de « Ce qui reste » de `2026-10-16-etape-9-maladie-sncf-et-mines.md`
— les avantages accessoires des pensions des mines, dont la majoration pour
enfants, que le dépôt laissait hors de l'assiette de la cotisation maladie
comme pour les complémentaires, sans l'avoir lu au décret. Les pages
(`pages.js`) étaient à la session 1 : rien n'y est écrit.

**Ce que disent les textes, lus le jour même dans l'index LEGI.**

- *L'article 91* du décret n° 46-2769 (LEGIARTI000037456798) prend 0,50 %
  des pensions « ainsi que leurs avantages accessoires, à l'exception de ceux
  mentionnés aux articles 139 et 141 », et 3,70 % au non-résident, avec la
  même exception. Toutes ses rédactions la portent depuis celle du
  30 décembre 1997 (LEGIARTI000006764900), qui fit passer le taux à 0,50 % au
  1er janvier 1998 ; celles de 1993 à 1997, de 3,30 % à 3,85 %, prenaient
  « les avantages mentionnés au 2° » de L. 711-2, sans exception écrite.
- *L'article 139* (LEGIARTI000006765039) : la majoration d'un dixième pour
  trois enfants, celle que le modèle sert aux mines ; *l'article 141*
  (LEGIARTI000031137571) : l'allocation pour enfant à charge. Exceptés.
- *Restent dans l'assiette* : la majoration de 0,15 % par trimestre au fond
  (art. 138, LEGIARTI000006765036) et celle du conjoint à charge (art. 140,
  LEGIARTI000031137566), que le modèle ne sert pas (fiche `pension_mines`).

**Ce qui est fait.** Rien ne change au calcul : l'exclusion du dépôt est
celle du texte. Elle est désormais fondée là où elle s'écrit : la donnée
(`prelevements_remuneration.yaml`, `maladie_regimes_speciaux`), la
docstring de `part_des_regimes_speciaux` (`contexte.py`) et de son jumeau
(`contexte.js`), la fiche `cotisation_maladie_des_non_residents` (les
articles 139 et 141 cités, une lecture, l'écart récrit : il ne reste que les
articles 138 et 140 non servis) ; le cliquet des rédactions sans statut
(`perimetre.yaml`) descend à 9 736. Le test
`test_la_majoration_des_mines_reste_hors_de_leur_cotisation`
(`test_net_pensions.py`) : un mineur né en 1960, parti en 2020, trois
enfants, paie 0,50 % de sa pension des mines, soit 0,4545 % de sa pension
majorée.

**Ce que montrent les mesures.** Rien ne bouge : ni les témoins ni le site.
Seuls les chiffres ancrés du poids du site (`README.md`) prennent le kilo-octet
des commentaires, que GitHub refait.

**Ce qui reste.**

1. *À une session des pages* : les deux retouches de `pages.js` (la
   réversion au plafond de moitié, l'assiette de chaque étage), inchangées.
2. *Le plafond de 2027* de la SNCF, inchangé.
3. *Les articles 138 et 140*, s'ils sont un jour servis (fiche
   `pension_mines`), entreront dans l'assiette des mines d'eux-mêmes : ils
   s'ajouteraient à la ligne du régime, non à la majoration pour enfants.
4. *L'histoire* (`prelevements_historiques.yaml`, `maladie_mines`) prend ses
   taux d'avant 1998 sur la pension sans la majoration, quand le texte d'alors
   n'écrivait pas l'exception : non mesuré, à voir avec la limite 5 ante ter.
