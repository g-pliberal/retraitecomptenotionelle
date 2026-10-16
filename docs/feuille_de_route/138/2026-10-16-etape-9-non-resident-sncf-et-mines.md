# Étape 9, suite de la huitième partie : le non-résident de la SNCF et des mines, à ses taux de L. 131-9

**La demande.** Vague ter du 16 octobre 2026, session 6 sur 13 : le point 2
de « Ce qui reste » de `2026-10-16-etape-9-maladie-sncf-et-mines.md` — le
retraité qui réside hors de France, dont la France prend en charge les soins,
et dont la SNCF ou les mines servent la pension. Les pages (`pages.js`)
étaient à la session 1 : rien n'y est écrit.

**Ce que disent les textes, relus le jour même dans l'index LEGI.**

- *La SNCF* (décret n° 2007-1056, art. 7, IV, second alinéa,
  LEGIARTI000052041125) : pour les pensionnés « relevant de l'article L. 131-9 »,
  « 3,90 % du montant trimestriel de la pension de retraite inférieur au
  plafond » et « 3,20 % du montant trimestriel de la pension de retraite
  supérieur à ce plafond ». Le plafond est celui des résidents (5 128 € de
  2010, revalorisé, de moitié pour une réversion, VII).
- *Les mines* (décret n° 46-2769, art. 91, LEGIARTI000037456798) : 3,70 %
  des pensions de vieillesse, d'invalidité et de réversion et de leurs
  avantages accessoires, hors ceux des articles 139 et 141, sans plafond.
- Ces taux remplacent ceux des résidents (0,70 %, 0,50 %) et ne suivent
  aucune tranche de CSG, comme ceux de D. 242-8.

**Ce qui est fait.**

- *La donnée* (`prelevements_remuneration.yaml`, `maladie_regimes_speciaux`) :
  `taux_non_resident` et `taux_non_resident_au_dela` de chaque régime.
- *Le modèle* (`remuneration.py`, `contexte.py`, et leurs jumeaux
  `remuneration.js`, `contexte.js`) : `MaladieRegimeSpecial.cotisation`
  prend, au non-résident, son taux sous le plafond et celui d'au-delà ;
  `Montants.du_foyer` ajoute, au non-résident couvert, la part de la SNCF et
  des mines dans la pension, que `net_d_assiette` et `net_d_un_depart`
  reprennent ; `pension_du_regime` la prend sur la ligne de son régime, au
  plafond de moitié pour une réversion. Le non-résident que la France ne
  couvre pas ne paie toujours rien.
- *La fiche* `cotisation_maladie_des_non_residents` : les deux décrets, les
  trois taux, l'écart restreint aux autres régimes spéciaux, à la fonction
  publique et aux indépendants ; le cliquet des rédactions sans statut
  (`perimetre.yaml`) descend d'une, l'article 91 étant désormais cité.
- *Les tests* (`test_net_pensions.py`) : les deux moteurs aux taux du
  non-résident sur les cinq pensions du test croisé ; un résident d'Espagne
  paie 3,9 % sur une ligne de la SNCF, 3,7 % sur une des mines.

**Ce que montrent les mesures.** Les témoins ne bougent pas : aucun cas type
ne réside hors de France. Un agent de la SNCF résidant en Espagne, couvert,
paie 3,90 % de sa pension sous le plafond, 3,2 % au-delà, au lieu de rien.

**Ce qui reste.**

1. *À une session des pages* : les deux retouches de `pages.js` de la note
   du 16 octobre (la réversion au plafond de moitié, l'assiette de chaque
   étage), qui valent aussi pour le non-résident.
2. *Les avantages accessoires* des mines, et le *plafond de 2027* : points 3
   et 4 de la note du 16 octobre, inchangés.
3. *L'histoire* (`maladie_des_pensions.py`) ne distingue pas le non-résident,
   pas plus que pour les autres régimes : le site seul le prélève.
