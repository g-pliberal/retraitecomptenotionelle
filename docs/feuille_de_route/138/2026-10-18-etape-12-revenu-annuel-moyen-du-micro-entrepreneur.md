# Étape 12, sixième partie : le revenu annuel moyen du micro-entrepreneur, fait de son revenu cotisé

**Le 18 octobre 2026, la demande.** Deuxième vague du 17 octobre, lancée par
la session d'orchestration : du micro-entrepreneur, le salaire annuel moyen
(le 4 de « Ce qui reste » de `…-micro-entrepreneur-avant-2023.md`, le 2 de
`…-trimestres-du-micro-entrepreneur.md`), puis l'arrondi s'il tient dans
l'étape, puis les clefs de 2016 et de 2017 si leur texte se trouve. Avant, le
revenu cotisé validait les trimestres, et le revenu abattu entrait au revenu
annuel moyen.

**Ce que dit le droit** (journal de veille,
`2026-10-18-action-138-etape-12-revenu-annuel-moyen-du-micro-entrepreneur.yaml`).

- *Le texte.* Le revenu de chaque année est « celui correspondant, pour
  chaque année prise en compte, aux cotisations versées par l'assuré au titre
  de cette année » (R. 351-29, I, B, que D. 634-3 applique aux indépendants
  depuis 2026) ; de 2019 à 2025, le revenu annuel moyen « correspond aux
  cotisations versées » (R. 634-1). L. 613-7, II calcule les prestations
  « sur la base » du chiffre d'affaires abattu : la caisse le cite en tête du
  point 4 de sa circulaire n° 2024-23, et le lit par le forfait payé.
- *La caisse.* De la part du forfait affectée au régime de base, le « Revenu
  cotisé de l'année concernée » (circulaire Cnav n° 2024-23, annexe 2) ; le
  revenu annuel moyen tient compte « des revenus cotisés à l'ex-régime social
  des indépendants » (exposé « Revenu annuel moyen »).
- *Le RSI.* En 2009, « cotisation RVB / taux RVB », la cotisation payée et
  compensée, au moins celle d'un trimestre sur une année civile entière
  (« 966 / 290 ») ; et, quand le forfait passe la cotisation de droit commun,
  sa part (« RAM : 543 / 16,65 % = 3 261 € au lieu de 2 610 € ») (circulaire
  n° 2009/024, point III). De 2010 à 2015, « (cotisation RVB année N réglée
  par l'assuré + compensation RVB année N) / taux de cotisation RVB de l'année
  N » (circulaires n° 2010/034, point III, B, et n° 2013/020, point 3.2).

**Ce qui est fait.**

- *Les deux moteurs* : `revenu_cotise` (l'ancien `_revenu_validant`, rendu
  public ; `revenuCotise`, exporté, `carriere.js`) donne aussi le revenu que
  `assiette_de_reference` (`assietteDeReference`, `droit/liquider.js`) porte
  au compte pour une ligne de micro-entrepreneur : le revenu qui valide ses
  trimestres entre à son revenu annuel moyen, plancher de 2009 et seuils de
  2010 à 2015 compris.
- *Tests* : `test_micro_social.py`, le revenu annuel moyen de 40 000 € de
  ventes en 2023 et en 2026, posé à la main depuis D. 613-4, D. 613-6 et
  D. 633-3, l'exemple de la circulaire (« 1 802,82 € » en 2023, à l'arrondi
  près) et le plancher de 2009 (200 × 8,71 €) ; `moteur.test.js`, les mêmes
  dans le portage, vus rouges contre l'ancien code.
- Fiche `micro_social_abattement`, régime `micro_entrepreneurs`, statut
  d'`affiliations.yaml` et inventaire, récrits. Les sept rédactions que la
  fiche citait depuis le 17 octobre sans être inscrites entrent à la liste des
  textes ; D. 131-6-4 de 2016, la cotisation du conjoint collaborateur, à
  rattacher, celui de 2019 sans effet ; le cliquet descend à 9 711.

**Mesuré.** Le revenu porté au compte, rapporté au revenu abattu : vente
0,9988 en 2023 et 2024, 0,9921 en 2025, 1,0313 en 2026 ; services 0,9985,
0,9918 et 1,0309 ; libéral 0,9996, 1,0002, 0,9928 et 1,0071 ; de 2018 à 2021,
1,0024, 1,0005 et 0,9996. 40 000 € de ventes portent 11 963 € au compte en
2026, au lieu de 11 600 € ; 3 000 € en 2009, sur l'année entière, 1 742 €,
au lieu de 870 €. Les quatre témoins du micro-entrepreneur de l'Assurance
retraite gagnent de 0,19 % (libéral) à 1,21 % (vente) au scénario 1, et
bougent de moins de 0,03 % aux scénarios 3 et 5 ; ceux de la Cipav, liquidés
en points, ne bougent pas, ni aucun autre témoin.

**L'arrondi, léger, reste déclaré.** La caisse arrondit à l'euro chaque
forfait déclaré, du mois ou du trimestre (« 273,06 € arrondis à 273 € »),
puis la somme des parts de l'année (« 319,76 arrondis à 320 ») : trois euros
au plus de part de base sur l'année, sous douze déclarations mensuelles, soit
dix-sept euros de revenu cotisé ; 1 801,66 € au lieu de 1 802,82 € dans
l'exemple, déclaré par trimestre. Le reproduire demanderait la
périodicité des déclarations et la répartition du chiffre d'affaires entre
elles, que la saisie ne demande pas ; il ne compte qu'au seuil d'un
trimestre. Léger au sens de la coupe du 14 octobre : la fiche le déclare.

**Les clefs de 2016 et de 2017, introuvables.** La base de la Cnav, par sa
recherche : la circulaire RSI n° 2015/006 (point D) donne les taux globaux
de 2016 et 2017, 13,4 %, 23,1 % et, pour la Cipav, 22,9 puis 23 %, sans
clef ; le barème « Taux de répartition par risques » commence au
1er octobre 2022.

**Trouvé en chemin.** Le barème de la Cnav « Chiffre d'affaire des
micro-entrepreneurs validant un trimestre » (source Urssaf Caisse nationale)
donne les seuils de 2017 à 2019, et ils ne suivent aucune clef constante :
4 085 €, 7 185 €, 10 250 € et 20 430 € de ventes pour un à quatre trimestres
en 2018, quand la clef de la circulaire n° 2025-20 (40,31 %) en demande
5 098 €, 10 197 €, 15 295 € et 20 393 € ; en 2017, 3 510 € pour un trimestre,
quand le revenu abattu en demande 5 048 €. Le quatrième seul tombe sur la
règle du modèle. Deux sources de la caisse divergent donc pour 2018 et 2019 ;
la règle qui fait ces seuils (une clef selon le chiffre d'affaires ?) reste
à lire.

**Ce qui reste.**

1. *Les seuils de 2017 à 2019* : la règle qui les fait, chez l'Urssaf ou dans
   les circulaires du RSI de 2016 à 2019 ; puis la validation de ces années.
2. *Les clefs de 2016 et de 2017*, et celles de janvier à septembre 2022.
3. *La Cipav avant 2023* : la règle de la CNAVPL.
4. *Qui ne relevait pas de la maladie du RSI* : en 2014 et 2015, le trimestre
   dès 150 heures ; de 2009 à 2015, la part du forfait quand il passe la
   cotisation de droit commun.
5. *La même classe d'erreur, ailleurs* : les points du RCI, et ceux de la
   CNAVPL pour la Cipav, se calculent au barème sur le revenu abattu, non sur
   la part du forfait qui les achète ; la seconde pension d'un
   micro-entrepreneur en cumul emploi-retraite additionne encore son revenu
   abattu (`droit/seconde.py`, `seconde.js`), la règle de l'indépendant
   restant à lire (D. 634-3 écarte le III de R. 351-29).
6. D. 131-6-3 ; l'arrondi, déclaré.
