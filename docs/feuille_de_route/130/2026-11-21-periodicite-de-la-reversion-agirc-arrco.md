# La réversion de l'Agirc-Arrco attend le terme de la période du défunt payé au trimestre ou à l'année

Domaine de la réversion (§ 11), écart laissé à sa clôture : « la réversion
minorée de l'Agirc et la périodicité du paiement ». Trois exemples de la
fédération, François, David et Simone, étaient en écart connu depuis le
28 septembre 2026 : le modèle servait toute retraite au mois, et faisait partir
la réversion un à dix mois trop tôt. Patch préparé hors de `main`, à relire
avant publication.

**Le texte, lu dans l'index KALI** (à jour du 13 novembre 2026), accord
national interprofessionnel du 17 novembre 2017 (KALITEXT000036731682) :

- article 106 (KALIARTI000036731860 du 1er janvier 2019 ; KALIARTI000047205218
  du 1er janvier 2021) : « Les allocations sont versées d'avance (terme à
  échoir) : a) mensuellement en France ainsi que dans les pays suivants » —
  trente-deux États, trente-cinq en 2021, qui ajoute Andorre, la Croatie et
  l'État de la Cité du Vatican — ; « b) trimestriellement dans les autres
  pays. Toutefois, l'allocataire peut demander à percevoir ses allocations
  mensuellement » ;
- article 107 (KALIARTI000036731861) : au-dessus de « 100 points du régime »
  et sous « 200 points, l'allocation est versée annuellement » ; à 100 points
  au plus, le versement unique, que la fiche `versement_unique_agirc_arrco`
  sert déjà ;
- article 116 (KALIARTI000036731971) : la réversion des droits d'un allocataire
  prend effet « au premier jour du mois ou du trimestre civil suivant le décès
  selon que les allocations de droits directs ont été respectivement versées
  mensuellement ou trimestriellement » ; ceux d'un participant non encore
  allocataire, « au premier jour du mois civil suivant le décès ».

**La pratique de la caisse**, circulaire 2020-02-DRJ, fiche 5, III : le
trimestre tient à « sa domiciliation bancaire » ; les seuils de l'article 107
s'apprécient « au regard du montant brut des droits directs [...], y compris
les montants des différentes majorations ou coefficients applicables ».
L'article 116 ne dit pas l'année : l'exemple de Simone, payée par an, morte le
6 février 2024, dont la réversion part le 1er janvier 2025, la date.

**Ce qui change.** Pour un décès depuis 2019 (version `accord_2017`), la date
d'effet part du premier jour de la période qui suit le décès :

- l'année suivante, quand l'allocation du défunt — les régimes de la fiche
  ensemble, majoration pour enfants comprise — fait plus de 100 et moins de
  200 points, au point de la fin de l'année des montants ;
- le trimestre civil suivant, quand le défunt réside hors de France et des
  États que l'article 106 nomme à la date du décès (présomption neuve
  `paye_dans_l_etat_de_residence` : la banque dans l'État de résidence, sans
  l'option du paiement mensuel) ;
- le mois suivant, sinon, et toujours pour le défunt mort avant son départ.

L'âge du survivant, son invalidité et ses deux enfants à charge jouent comme
avant, à partir de cette date. Code : `periodeSuivante` et
`allocationDuDefunt`, dans `moteur/js/droit/reversion.js` ; paramètre
`periodicite` de la version `accord_2017`.

**Les exemples.** Le témoin prête à Perla, Kevin et David une résidence aux
États-Unis, seule voie du paiement trimestriel que le texte ouvre, et à
Simone une carrière de seize mois (`age_debut: 60.75`), 180 points en 2024 :
François (1er janvier 2025), David (1er octobre 2024) et Simone (1er janvier
2025) concordent ; Eric, dont l'âge vient après le trimestre, concorde
toujours. Le test d'abord : les trois exemples, sans leur écart connu, vus
rouges pour la date attendue ; treize cas posés à la main dans
`tests/test_reversion.py` (le trimestre selon l'État, les 200 points de part
et d'autre, la majoration comptée, l'Arrco et l'Agirc ensemble, la Croatie
avant et depuis 2021, le décès d'avant 2019 et celui de l'actif).

**Ce qui reste**, déclaré dans la fiche : avant 2019, les règlements de
l'Arrco et de l'Agirc ne sont pas lus — ils payaient par trimestre avant leur
mensualisation, et la réversion d'un décès d'alors peut partir jusqu'à deux
mois trop tôt ; la périodicité se mesure à l'année du décès, quand la caisse
la fixe à la liquidation ; l'allocation de 100 points au plus encore servie
est présumée payée au mois. La réversion elle-même, de 100 points au plus,
devrait être versée en capital au survivant (article 107) : non portée.
