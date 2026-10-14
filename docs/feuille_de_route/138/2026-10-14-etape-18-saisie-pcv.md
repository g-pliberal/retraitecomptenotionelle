# Étape 18, troisième partie : la saisie des PCV — la sage-femme, le biologiste, le secteur 2 du médecin

**La demande.** Session du site du 14 octobre 2026, point b : distinguer la
sage-femme du chirurgien-dentiste, le biologiste du pharmacien et le secteur du
médecin, que la deuxième partie (`2026-10-14-etape-18-cotisations-pcv.md`)
avait présumés ; la règle et le champ ensemble, dans les deux moteurs.

**Le champ.** Trois statuts de plus au menu, que la saisie, les deux contextes
et l'adresse lisent comme les autres, puisqu'ils viennent d'`affiliations.yaml`
: `sage_femme`, `biologiste_liberal`, `medecin_liberal_secteur_2`. Le code
`chirurgien_dentiste_ou_sage_femme` garde son nom, que des adresses portent,
mais son libellé devient « Chirurgien-dentiste libéral » ; `pharmacien`,
« Pharmacien libéral » ; `medecin_liberal`, « Médecin libéral en secteur 1 ».
Le menu passe de 68 à 71 statuts ; le README le dit.

**La règle**, lue dans l'index LEGI du 11 octobre et au guide de la CNAVPL de
2025, p. 85 et 90 à 94.

- *La sage-femme* (fiche `asv_sages_femmes`) : dix-huit points par année de
  cotisation (décret n° 84-254, article 3), un forfait sans ajustement, dont
  elle paie le tiers — 229 € de 2008 à 2011 (D. 645-2), 687 à 780 € au total
  depuis 2012 (décret n° 2011-2002) —, 6,10 € le point ; taux plein à 67 ans,
  minoration de 1,25 % par trimestre bornée à douze, 10 % pour trois enfants.
  Sa complémentaire reste celle de la CARCDSF.
- *Le biologiste non médecin* (fiche `asv_directeurs_laboratoire`) : 262
  points par forfait, cinquante au plafond d'ajustement, 0,30 % puis 1,2 %
  depuis 2022 (décret n° 2007-597) ; le tiers du forfait et la moitié de
  l'ajustement à sa charge ; 0,3927 € le point acquis depuis 2006, en 2025.
- *Le médecin de secteur 2* : les mêmes régimes et les mêmes points ; mais il
  paie seul le forfait et l'ajustement, 5 556 € et 3,80 % en 2025. Un champ
  d'affiliation neuf, `sans_prise_en_charge_depuis: 1980`, lu par
  `Affiliations.sans_prise_en_charge` (jumelle `sansPriseEnCharge`) : le
  compte porte alors la cotisation entière comme la sienne, sous toutes les
  conventions. Le paquet ne l'écrit que pour ce statut, et garde sa version.

**Les présomptions**, déclarées dans les fiches : avant 2008, les points et le
forfait de la règle de 2008, projetés en arrière sur les prix ; les forfaits
fixes en euros projetés sur les prix entre deux textes ; les valeurs de
service des points d'avant 2006 non servies ; le coefficient d'anticipation du
biologiste, que le guide ne chiffre pas, à 1,25 % par trimestre ; la CARSAF
d'avant 2009 ; l'OPTAM du secteur 2.

**Ce que montrent les mesures**, une assurée née en 1960, au salaire moyen de
25 à 65 ans : la sage-femme reçoit 4 008 € de PCV par an (720 points à 6,10 €,
minorés de 8,75 %), quand le statut commun lui en servait 10 576, ceux du
dentiste. Aucune pension des 816 témoins ne bouge ; vingt et un témoins neufs.

**Ce qui reste**, au propriétaire ou à une session de données : les règlements
des sections approuvés le 10 juillet 2026 ; les forfaits et les points d'avant
2008 ; un exemple chiffré publié à rejouer.
