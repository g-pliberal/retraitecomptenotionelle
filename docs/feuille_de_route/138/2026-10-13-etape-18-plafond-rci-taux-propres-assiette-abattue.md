# Étape 18, première partie : le plafond propre du RCI, le barème propre des artisans et l'assiette abattue

**Reprise, au 18 octobre 2026.** Fait : le plafond propre du RCI, le barème
propre des artisans, l'assiette abattue (13 octobre) ; les cotisations PCV et
leur saisie, les points d'avant 1973 (14 octobre) ; les points d'invalidité,
le conjoint collaborateur, les dispenses de l'assiette minimale (16 octobre) ;
la Lodeom (17 octobre) ; les champs de saisie des dispenses, de la Lodeom et de
l'option du conjoint collaborateur, le forfait par défaut (18 octobre, notes
`…-saisie-des-dispenses.md` et `…-champs-de-la-lodeom-et-du-collaborateur.md`).
Reste, une session : au fac-similé, les classes d'avant 1973. Au propriétaire, à
confirmer : ce forfait par défaut, que la note prévoyait. CAVEC, CNBF : action
131 ; Mayotte : 121.

**La demande.** Le propriétaire, le 13 octobre 2026 : « Action 138, étape 18,
pas encore commencée : commence par l'assiette abattue des indépendants, leurs
taux propres et le plafond du RCI. Laisse les grilles de la CAVEC et de la CNBF
(action 131) et Mayotte (action 121), que d'autres sessions tiennent. »
`castypes.py`, `cas_types_csp.yaml`, `grille_large.py` (action 152), `cout.py`
(action 147), `pages.js` et `index.html` n'ont pas été touchés.

**Ce que disent les textes, lus le jour même** dans l'index LEGI du dépôt,
mis à jour de l'incrément du 12 octobre.

- *Le plafond du RCI.* D. 635-7 arrête la première tranche (7 %) à un plafond
  propre au régime : celui de la sécurité sociale du 1er janvier 2013, puis
  « indexé sur la dernière valeur du revenu de référence, dans la limite du
  coefficient annuel de revalorisation des pensions » (rédactions de 2013 et
  2017), puis revalorisé « du plus petit » des deux coefficients (rédaction du
  25 mai 2020) ; la seconde tranche (8 %) part de lui jusqu'à quatre plafonds
  de l'année. La caisse publie le montant : 38 493, 38 916, 40 784 et 42 946 €
  de 2021 à 2024 (circulaires Cnav 2020-42, 2021-36, 2022-37, 2023-33) ; avant,
  37 032 € en 2013, 37 513 € en 2014 et 2015, 37 546 € en 2016 et 2017,
  37 846 € en 2018, 37 960 € en 2019 et 38 340 € en 2020, lus chez l'IPP,
  Harvest, Legisocial, dans la brochure du RSI de 2016 et le barème 2020 de la
  CPS de Saint-Barthélemy. La rédaction du 7 juillet 2024, pour les périodes
  courant depuis 2025, coupe au plafond de la sécurité sociale ; les
  circulaires 2024-36 et 2025-31 publient pourtant un plafond propre pour 2025
  et 2026 (43 891 et 44 286 €) en citant la rédaction remplacée. Le dépôt suit
  le texte, et la fiche le range parmi les lectures divergentes.
- *Le barème propre.* D. 633-3, créé le 1er janvier 2014 (il portait jusqu'en
  2008 une autre règle) : 16,95 % sous le plafond et 0,20 % sur la totalité en
  2014, 17,05 % et 0,35 % en 2015, 17,15 % et 0,50 % en 2016 (dérogation en
  note), 17,15 % et 0,60 % ensuite, 0,72 % pour les périodes depuis 2025.
  Intégrés au régime général en 2018, l'artisan et le commerçant gardent ce
  barème : le dépôt leur prêtait celui du salarié et de son employeur, 15,45 %
  et 2,30 à 2,51 %, convention que les limites déclaraient.
- *L'assiette abattue.* Pour les périodes courant depuis 2025, l'assiette des
  cotisations et de la CSG de l'indépendant non agricole est son revenu avant
  cotisations abattu de 26 % (L. 136-3, III), l'abattement ni inférieur à
  1,76 % ni supérieur à 130 % du plafond (D. 136-5) ; elle inclut les revenus
  de remplacement et exclut l'épargne salariale (L. 131-6). Aucun exemple
  chiffré publié n'a été trouvé, ni pour elle ni pour les deux autres règles.

**Ce qui est fait**, en trois envois.

1. *Le plafond propre du RCI* (4404f54). Une période peut porter des bornes en
   euros année par année (`borne_basse_par_annee`, `borne_haute_par_annee`) ;
   `PeriodeRegime.bornes_assiette_en_euros` les lit, avec l'année, que ses
   appelants passent désormais — et refuse de s'en passer. Les points du
   scénario 1, le compte et la fiche de paie (`Segment` reçoit des bornes en
   euros) coupent ainsi `rci.yaml` de 2013 à 2024, dans les deux moteurs. Fiche
   `rci_seuil_premiere_tranche`, de `manquante` à `transcrite`.
2. *Le barème propre* (0cc72b3). Deux mesures `_non_salarie` du régime général
   dans `taux_cotisation_annuels.csv`, certifiées par un récupérateur neuf,
   `scripts/fetch/dila_legi_taux_independants.py`, qui lit les cinq rédactions
   de D. 633-3 dans l'index ; `PeriodeRegime.taux_du_cotisant` les rend à un
   assuré sans employeur, que le compte et la fiche de paie interrogent. Fiche
   `cotisation_vieillesse_independants`, source déclarée dans `sources.yaml`,
   limites et méthodologie récrites.
3. *L'assiette abattue* (3d68d1c). La règle est dans le profil `independant`
   de `prelevements_remuneration.yaml` ; `ProfilRemuneration.assiette_abattue`
   et `revenu_avant_abattement`, jumelles en JavaScript, passent du revenu brut
   à l'assiette et retour. La saisie et le revenu disponible n'en font rien
   encore : fiche `assiette_sociale_independants`, `approchee`, qui mesure ce
   qu'il en coûte.

Le paquet garde sa version 19 : les champs nouveaux ne s'écrivent que là où ils
servent, et le moteur JavaScript lit leur absence comme l'ancienne règle.
`tests/test_independants.py` tient les trois, jumeau compris.

**Ce que montrent les mesures.**

- *Le plafond du RCI* : la pension RCI d'un artisan né en 1960, parti à
  64 ans, gagne 0,2 à 0,5 % — 12 à 14 € par an — dès que son revenu passe le
  plafond propre ; rien en dessous. 60 000 € de revenu en 2019 cotisent
  4 420,40 € au lieu de 4 394,76 €.
- *Le barème propre* : rien sous le plafond jusqu'en 2023 (17,75 % des deux
  côtés), 0,12 point de moins en 2024 et 0,09 en 2026 ; au-dessus, 1,70 à
  1,79 point de moins sur la part qui le dépasse. Le système actuel ne bouge
  pas ; les comptes notionnels rétroactifs d'un artisan à deux fois le salaire
  moyen perdent 0,6 à 0,8 %, ceux du prospectif rien. Sa fiche de paie de 2019
  prélève 7 309,87 € sur 60 000 €, et non 7 640,96 €.
- *L'assiette abattue* : en 2026, pour une assiette de 20 000, 40 000 et
  80 000 € d'un artisan, la fiche de paie affiche 12 166, 22 947 et 47 315 € de
  revenu disponible, quand le revenu brut d'où vient l'assiette en laisse
  19 193, 37 001 et 75 423 € : 58 à 61 % de moins.

**Pour les pages**, que la session du site tient.

- `pages.js:5877-5879` dit l'assiette « votre revenu professionnel après
  l'abattement de 26 % » : l'abattement porte sur le revenu avant cotisations,
  et il est borné. Proposition : « votre revenu avant cotisations, diminué de
  26 % — l'abattement est d'au moins 1,76 % et d'au plus 130 % du plafond ».
- La saisie pourrait accepter ce revenu brut et le convertir en assiette par
  `profil.assietteAbattue(revenuBrut, plafond, annee)` (`remuneration.js`),
  pour les années depuis 2025 ; le relevé de carrière porte, lui, l'assiette.
- Le revenu disponible de l'indépendant se calcule sur l'assiette, et non sur
  le revenu brut : 58 à 61 % trop bas en 2026. Le corriger touche le net de la
  fiche de paie, que lisent les taux de remplacement nets et les indicateurs de
  cycle de vie (étape 9) : à faire d'un même geste, la page montrant le revenu
  brut (`profil.revenuAvantAbattement(assiette, plafond, annee)`) et la ligne de
  l'abattement.
- Les témoins de pages que GitHub refera montreront la fiche de paie des
  artisans changée : la ligne du régime général plus basse au-dessus du
  plafond, celle du RCI de 2013 à 2024.

**Pour l'action 131.** La fiche de paie ignore toujours les bornes fixes en
euros de la CNBF et de la CARPIMKO (`borne_basse_euros`, `borne_haute_euros`) :
elle ne connaît que celles en plafonds. Les bornes en euros que `Segment` reçoit
désormais pourraient les porter.

**Ce qui reste** de l'étape, une session par point, dans l'ordre du poids :
les cotisations PCV des professions de santé conventionnées (registre,
chantier 138.18) ; les points d'avant 1973 des artisans et des commerçants ;
les 400 points d'incapacité de la CNAVPL ; le conjoint collaborateur ; la
dispense de l'assiette minimale des activités saisonnières (L. 613-11) ; la
Lodeom. À relire : les publications du RSI de 2014, 2015, 2018 et 2019 ;
l'usage du plafond propre que la Cnav publie encore pour 2025 et 2026 ; un
exemple chiffré de l'assiette abattue. Les revenus de remplacement et l'épargne
salariale de l'assiette viendront avec la saisie d'un revenu brut.
