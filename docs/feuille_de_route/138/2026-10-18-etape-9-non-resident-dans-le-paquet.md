# Étape 9, suite de la huitième partie : les taux du non-résident de la SNCF et des mines, dans le paquet du site

**La demande.** Deuxième vague du 17 octobre 2026, lancée par la session
d'orchestration : le premier point du bloc « Reprise » de la huitième partie
(`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`), que la note du
17 octobre nomme (`2026-10-17-etape-9-cotisation-sncf-par-etage.md`, « Ce qui
reste », point 1) — les taux du non-résident, que le paquet du site ne
portait pas. Aucune source de droit relue : les taux sont ceux que la note du
16 octobre a lus (L. 131-9 ; décret n° 2007-1056, art. 7, IV, second alinéa ;
décret n° 46-2769, art. 91).

**Ce qui est fait.**

- *Le paquet* (`scripts/construire_donnees.py`, `_prelevements_remuneration`) :
  `maladie_regimes_speciaux` porte `taux_non_resident` et
  `taux_non_resident_au_dela` de chaque régime ; la version monte à 24 des
  deux côtés (`VERSION`, `VERSION_PAQUET`), et le paquet est refait.
- *Les tests* : `test_net_pensions.py`, la `PrelevementsPension` du portage
  lit dans le paquet fabriqué, champ par champ, ce que le modèle lit du
  fichier — la classe du défaut, non ses deux champs : les tests du portage
  lui donnent le fichier, le site lui donne le paquet, et un champ que le
  paquet oublie se lit à zéro ; `test_web.py`, la ligne sous le montant de
  l'agent de la SNCF venu du privé, résidant en Espagne, contre le calcul
  posé à la main : 3,90 % de sa pension de la SNCF sous le plafond, 3,20 %
  au-delà, 3,20 % de sa base, 4,20 % de sa complémentaire, ni CSG, ni CRDS,
  ni CASA.

**Ce que montrent les mesures** (l'agent du 17 octobre : né en 1970, cadre à
22 ans, à la SNCF à 45, parti à 65 au salaire moyen et demi, montants nets,
euros de 2026, résidant en Espagne sans pension espagnole) : 3 562 € par mois
sur le site, comme le Python (3 562,42 €), au lieu de 3 653 €. Ses 2 362,78 €
bruts de la SNCF paient 90,53 € — 3,90 % de 2 131,83 €, 3,20 % des
230,94 € au-delà —, et la ligne écrit 2 272 € de régime intégré au lieu de
2 363. Résidant en France, il garde ses 3 344 €. Aucun témoin ne bouge : les
trois cas à l'étranger, le Maroc des simulations et les deux pages en
Espagne, sont des salariés du privé non cadres. Deux tests du niveau site,
`test_les_temoins_du_portage_sont_a_jour` et
`test_le_portage_javascript_retrouve_les_chiffres_du_modele`, étaient rouges
avant ce changement, sur `HEAD` : le paquet et `simulations.json` attendaient
les commits venus depuis la dernière suite verte de GitHub (`d8af61d`) — 224
écarts sur 874 cas, du micro-entrepreneur, que le paquet refait efface ;
restent les clés de la contribution du FSPOEIE, dans `simulations.json`, que
la fabrique suivante refait.

**Ce qui reste**, une session par point :

1. *La réversion au plafond de moitié*, avec la réversion de la SNCF (note du
   17 octobre, point 2) : elle vaudra aussi pour le non-résident, dont le
   plafond est celui des résidents.
2. *Inchangés* : le plafond de 2027 ; la limite 5 ante ter (2), en fin
   d'étape ; la CNBF et la Cipav dans la fiche de paie ; les décrets qu'aucune
   marche ne rejoint ; au propriétaire, les décrets des exploitants de 1980 à
   1989, au fac-similé.
