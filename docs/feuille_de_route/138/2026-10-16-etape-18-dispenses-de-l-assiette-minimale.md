# Étape 18, sixième partie : les dispenses de l'assiette minimale des indépendants

**La demande.** La session n° 6 de la vague quater du 16 octobre 2026 :
« action 138, étape 18. Les dispenses de l'assiette minimale des artisans et
des commerçants, lues à la source et appliquées dans les deux moteurs ». La
Lodeom, les classes d'avant 1973 et le champ de saisie du conjoint
collaborateur restent à d'autres sessions. `pages.js`, la saisie et
`textes.py --inscrire` n'ont pas été touchés.

**Ce que faisait le dépôt.** L'assiette minimale du régime de base
(`assiette_minimale_independants.csv`, D. 633-2, D. 642-4) s'opposait à tout
artisan, commerçant ou libéral hors du micro-social ; la fiche
`assiette_minimale_independants` déclarait les dispenses sans les faire (coupe
du 14 octobre).

**Ce que disent les textes**, lus le jour même dans l'index LEGI, mis à jour au
15 octobre, et dans l'index JORF (détail au journal de veille du jour).

- *Le RSA et la prime d'activité.* Sauf demande contraire, les montants
  minimaux de la base des artisans et commerçants, de leur complémentaire, et
  de la base et des complémentaires des libéraux (L. 644-1, L. 644-2) ne
  s'appliquent pas aux bénéficiaires de L. 262-2 du code de l'action sociale
  et de L. 842-1 : L. 131-6-3, rétabli par la loi n° 2015-1702, art. 21, « aux
  périodes courant à compter du 1er janvier 2016 » ; L. 613-9 en 2018 ;
  L. 613-11 depuis. La demande contraire se fait avant le 31 octobre de l'année
  d'avant, tacitement reconduite (D. 613-7). Avant 2016, seule la cotisation
  minimale maladie en dispensait le RSA (D. 612-5, 2009).
- *L'activité accessoire saisonnière.* Ajoutée à L. 613-11 par la loi
  n° 2019-1446, art. 10, en vigueur le 28 décembre 2019, sans date d'effet
  propre ni décret qui la définisse.
- *Le libéral.* D. 642-4, de 2004 à 2015 : la cotisation minimale ne
  s'applique « ni aux personnes dont l'activité libérale n'est pas l'activité
  professionnelle principale, ni aux personnes bénéficiaires d'un avantage de
  retraite ou d'une pension d'invalidité ». La rédaction de 2016 ne le dit
  plus ; D. 633-2 ne l'a jamais dit de l'artisan.
- *L'application.* Bpifrance Création, au barème de 2026 : « les cotisations
  minimales ne s'appliquent pas aux personnes bénéficiaires du RSA ou de la
  prime d'activité », « sauf demande contraire ». L'Urssaf a refusé le réseau
  de la session. Aucun exemple chiffré publié.

**Ce qui est fait.** Une table, `legislation/dispenses_assiette_minimale.yaml` :
cinq motifs (`rsa`, `prime_activite`, `activite_saisonniere`,
`activite_non_principale`, `pensionne`), leurs années, leurs familles de
statuts, et s'ils écartent aussi le minimum des complémentaires des libéraux ;
le paquet la porte (`dispenses_assiette_minimale`), à version égale, le
JavaScript lisant son absence comme aucune dispense. Une ligne de relevé dit
son motif (`LigneRelevee.dispense_assiette_minimale`, jusqu'au fait de la
chronologie) ; `_ligne_annuelle` et son jumeau `ligneAnnuelle` le retiennent
les années où le texte dispense le statut — un motif hors de ses années est
sans effet, un motif inconnu refusé —, annulent alors l'assiette minimale de
la base, et `acquerir` comme le compte, dans les deux moteurs, écartent celle
des complémentaires des libéraux (la CARPIMKO depuis 2026, la CAVOM) quand le
motif les couvre. Fiche `assiette_minimale_independants`, qui reste
`approchee` (la saisie) ; le point du registre (modèle de l'Urssaf) passe de
`coupe` à `repris`. Cinq tests dans `tests/test_independants.py`, dont la
comparaison des deux moteurs, lignes et résultat entier, sur deux relevés.
Aucun témoin ne bouge : aucun relevé figé ne déclare de dispense.

**Ce que montrent les mesures** (scénario 1, née en 1962, 3 000 € par an de
1990 à 2025, départ à 65 ans).

- Artisane au RSA sur tout le relevé : 59 trimestres au lieu de 75 ; régime
  général, 684 € par an au lieu de 999 € ; RCI et RCO inchangés, qui n'ont pas
  de minimum. Avec l'ASPA, la pension servie ne bouge pas.
- Infirmière libérale : CNAVPL 2 444 € au lieu de 2 582 €, PCV 578 € au lieu
  de 729 € (ses points suivent les trimestres) ; de 2010 à 2026, sa CARPIMKO
  porte 30 862 € de cotisations revalorisées au lieu de 32 756 €, le
  demi-plafond de 2026 écarté.
- Le compte notionnel prospectif de l'artisane : 1 451 € au lieu de 1 802 €.

**Pour les pages**, que la session du site tient. Un champ servirait, par
année ou par plage d'un relevé ou d'un métier indépendant : « bénéficiaire du
RSA ou de la prime d'activité », « activité accessoire saisonnière »,
« activité libérale non principale » ou « déjà pensionné » (avant 2016),
qui écrit `dispense_assiette_minimale` sur les lignes ; le relevé de carrière
porte déjà le champ.

**Ce qui reste**, de ce point : un exemple chiffré de l'Urssaf ; si la
dispense saisonnière vaut dès les cotisations de 2019 ; le champ de saisie ;
le conjoint collaborateur à l'option sous l'assiette minimale (note du
conjoint). De l'étape, une session par point : la Lodeom ; au fac-similé, les
classes d'avant 1973.
