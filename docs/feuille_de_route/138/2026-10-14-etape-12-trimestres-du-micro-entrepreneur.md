# Étape 12, troisième partie : les trimestres du micro-entrepreneur, validés sur le versement

**Le 14 octobre 2026, la demande.** Une des dix-neuf sessions du jour, la
treizième : le premier reste du bloc de l'étape, le revenu qui valide les
trimestres du micro-entrepreneur, dans les deux moteurs, texte en main. Le
registre le disait de modele-ti et du dépôt (`referents.yaml`, chantier
« 138.12 ») : service-public valide sur le versement, le dépôt sur le revenu
abattu.

**Ce que dit le droit** (journal de veille,
`2026-10-14-action-138-etape-12-trimestres-du-micro-entrepreneur.yaml`).
L. 613-7, II calcule les prestations sur le chiffre d'affaires abattu ; mais la
circulaire Cnav n° 2024-23 (point 4) valide les trimestres sur un « revenu
cotisé » : le chiffre d'affaires fois le taux global (D. 613-4), fois le taux de
répartition de la retraite de base (D. 613-6), divisé par le taux de base des
indépendants (D. 633-3 : 17,75 % jusqu'en 2024, 17,87 % depuis), comparé à
150 SMIC horaires. D. 613-6 ne couvre l'Assurance retraite que depuis le décret
n° 2022-1529, au 1er octobre 2022. Pour la Cipav, la première tranche de la
CNAVPL. Service-public (F23369) en donne les exemples de 2026, la circulaire
ceux de 2023 et de 2024.

**Ce qui est fait.**

- *La table* `data/reference/legislation/micro_social.yaml` : par activité,
  les versions de D. 613-4, D. 613-6 et D. 633-3 lues dans l'index, du mois où
  elles s'appliquent. `charger_validation_micro` en tire, par année, le
  rapport du revenu cotisé au revenu abattu, moyenne des douze mois (2024
  change au 1er juillet pour le libéral et la Cipav) ; seules les années
  couvertes entières y sont, de 2023 à 2026, la dernière valant au-delà. Le
  paquet le porte (`validation_micro`).
- *Les deux moteurs* : le métier (`Metier.micro`), la chronologie et la ligne
  (`AnneeCarriere.micro`) portent l'activité, que la saisie y met quand elle
  abat ; `_revenu_validant` (`revenuValidant`) convertit le revenu de la ligne
  avant le décompte, et l'assiette minimale ne touche plus la ligne.
- *Mesuré, en 2026* : 12 100 € de ventes valident deux trimestres, et non un ;
  services, trois ; libéral, quatre, comme avant ; 2 793 € de recettes à la
  Cipav, un, et non les trois que l'assiette minimale du libéral lui donnait à
  tort. En 2025, la vente valide moins qu'avant (0,288 du chiffre d'affaires
  contre 0,29) : le taux de base monte sans que la part suive. Les 816 témoins
  ne bougent pas ; deux de plus (`micro_entrepreneur_vente_au_seuil`, qui perd
  un trimestre en 2025, et `_cipav_petites_recettes`, 59 trimestres au lieu
  de 78), que le portage retrouve au bit près. `tests/test_micro_social.py`
  rejoue les exemples de F23369 et de la circulaire.
- Fiche `micro_social_abattement`, régime `micro_entrepreneurs`, statut
  `micro_entrepreneur` d'`affiliations.yaml` et écart du registre, récrits.

**Ce qui reste.**

1. *Avant le 1er octobre 2022*, le revenu abattu valide : la règle d'alors
   (circulaire n° 2023-4 et devancières, seuils de L. 133-6-8-2 de 2010 à 2015)
   reste à lire.
2. *Le salaire annuel moyen* garde le revenu abattu, comme L. 613-7, II le dit ;
   la circulaire parle des « droits » déterminés par le forfait payé : lire ce
   que la caisse reporte au compte.
3. *La cotisation des comptes notionnels* (le 2 de
   `2026-10-14-etape-12-micro-entrepreneur.md`) ; le RCI
   en points sur sa part du forfait (19,75 % en 2026), que la circulaire
   décrit et que le modèle prend au barème.
4. *L'arrondi* : la caisse arrondit chaque versement trimestriel ; le modèle
   prend l'année entière.
