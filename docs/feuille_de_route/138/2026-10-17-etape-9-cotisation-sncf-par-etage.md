# Étape 9, suite de la huitième partie : la cotisation de la SNCF et des mines, étage par étage, sur la page des résultats

**La demande.** Vague du 17 octobre 2026, session 10 sur 12 : les deux
retouches de `pages.js` que le bloc « Reprise » de la huitième partie
(`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`) réserve à une session
des pages, et que la note du 16 octobre nomme
(`2026-10-16-etape-9-maladie-sncf-et-mines.md`, « Ce qui reste », point 1) :
la réversion au plafond de moitié, et l'assiette de la SNCF et des mines de
chaque étage. Aucune source de droit relue : les textes sont ceux de ces
notes (décret n° 2007-1056, art. 7, IV et VII ; décret n° 46-2769, art. 91).

**Ce qui est fait : les étages.**

- *Le modèle* (`contexte.py`, puis son jumeau `contexte.js`) :
  `net_d_assiette` et `pension_d_assiette` reçoivent, avec `lignes`, la
  pension de chaque régime que la part contient, majoration pour enfants
  exclue, et prennent la cotisation de la SNCF et des mines sur les leurs,
  sous le plafond ; sans `lignes`, au prorata de `brut`, exacte sur un total,
  comme `pension_servie` et `net_d_un_depart` la gardent.
  `_maladie_des_regimes_speciaux` porte, pour elles et pour
  `pension_du_regime`, la condition qui la rend due : la tranche du foyer
  prélève la maladie, ou la France soigne le non-résident.
- *La page* (`pages.js`) : `etagesActuels` rend aussi les `lignes` de chaque
  étage, et `compositionActuelle` les passe ; le minimum vieillesse n'en a
  pas.
- *Les tests* : `test_net_pensions.py`, les deux moteurs sur trois foyers —
  le taux plein, le taux réduit, le non-résident — et cinq parts, l'étage de
  l'agent de la SNCF, celui d'un mineur, le prorata sans lignes ;
  `test_web.py`, la ligne sous le montant d'un agent de la SNCF venu du privé,
  contre le calcul posé à la main.

**Ce que montrent les mesures** (né en 1970, cadre à 22 ans, à la SNCF à 45,
parti à 65 au salaire moyen et demi, montants nets, euros de 2026) : 3 344 €
par mois, comme avant ; sous le montant, 2 133 + 741 + 470 € au lieu de
2 138 + 737 + 469 € — 2 362,78 € bruts de la SNCF, au-dessus du plafond de
2 131,83 € par mois, paient seuls les 14,92 € de la cotisation. Aucun témoin
ne bouge : aucun cas type n'a la SNCF ni les mines à côté d'un autre étage.

**Ce qui n'est pas fait : la réversion.** La réversion de la SNCF n'est pas
portée : la table des réversions n'a pas de fiche pour elle, et sa ligne vaut
0 € (« non calculée : ce régime n'est pas encore porté ») ; celle des mines
n'a pas de plafond. Passer `reversion = true` à `pensionDuRegime` n'aurait
rien à montrer, ni aucun test à voir rouge : la retouche attend la réversion
de la SNCF. Elle ne vaudra que pour la colonne « Sa réversion » : `mensuel`
sert aussi « Votre pension », celle du défunt, qui garde le plafond entier.

**Un défaut trouvé : le paquet du site ne porte pas les taux du
non-résident.** `scripts/construire_donnees.py` écrit
`maladie_regimes_speciaux` sans `taux_non_resident` ni
`taux_non_resident_au_dela`, que `remuneration.js` lit à 0 faute d'eux : sur
le site, le même agent résidant en Espagne, que la France soigne, ne paie
rien à la SNCF — 3 653 € nets par mois, quand le Python, qui lui prend 2,45 %
de sa pension, en donne 3 562. Les tests du non-résident lisent
`prelevements_remuneration.yaml`, non le paquet. La correction change la
structure du paquet : deux champs, `VERSION` et `VERSION_PAQUET` à 24, le
paquet refait.

**Ce qui reste**, une session par point :

1. *Le paquet du site* : les deux taux du non-résident dans
   `maladie_regimes_speciaux`, la version des deux côtés, et le test qui
   confronte au paquet ce que `PrelevementsPension` en lit.
2. *La réversion au plafond de moitié*, avec la réversion de la SNCF.
3. *Inchangés*, de la huitième partie et de ses suites : le plafond de 2027 ;
   la limite 5 ante ter (2) ; la CNBF et la Cipav dans la fiche de paie ; les
   décrets qu'aucune marche ne rejoint ; au propriétaire, les décrets des
   exploitants de 1980 à 1989, au fac-similé.
