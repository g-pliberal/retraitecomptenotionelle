# Étape 2, troisième partie : le personnel navigant, les députés et Mayotte, lus et mis en fiches

**Le 14 octobre 2026 : trois fiches de règles, toutes `approchee`, pour trois
régimes calculés qui n'avaient que la fiche générique de liquidation —
`crpn_pension_des_navigants` (les deux tranches de la caisse des navigants),
`deputes_pension_des_anciens_deputes` et `mayotte_pension_de_base`. Aucun
moteur, aucun chiffre ne bouge. La lecture corrige ce que les fiches de régime
disaient de chacun : un taux d'appel écrit, une part de l'Assemblée écrite, une
formule de 1987 écrite.**

Demande du propriétaire, ce 14 octobre : « action 145, étape 2, l'outre-mer, le
personnel navigant et les assemblées, que la clôture de l'action 121, ce matin,
ouvre. Documentés, non calculés, comme les fiches déjà faites de l'étape ».

- *La méthode.* L'index LEGI du dépôt, mis à jour au 13 octobre, et l'index
  JORF, lus article par article, rédaction par rédaction ; hors de l'index, le
  seul règlement de la caisse des députés, sur le site de l'Assemblée (copie
  datée, empreinte dans la fiche), que le Journal officiel publie aussi.
- *La caisse des navigants.* R. 426 du code de l'aviation civile, de 1984 à
  2023, puis R. et D. 6527 du code des transports. Cinq versions : vingt-cinq
  annuités au plus et liquidation dès quarante-cinq ans aux coefficients de
  0,65 à 0,95 (1984) ; la durée du taux plein liée à la réserve N du fonds
  (1995) ; cinquante ans et vingt annuités, décote de 5 % par année sur l'âge et
  la durée (2012) ; la durée seule (2022) ; la valeur « a » remplacée par les
  jours cotisés (2027). Elle couvre `navigants_2012` et `navigants_2022`.
- *Les députés.* Le règlement, lu en entier, est publié au Journal officiel du
  4 janvier 2018 et modifié par les arrêtés du Bureau de 2023 et de 2026, eux
  aussi publiés. Trois versions, à la génération, comme l'article 21 ter :
  les valeurs de 2008 (nés avant 1949), celles de l'âge d'ouverture (1949 à
  1968), celles du soixante-quatrième anniversaire (1969 et après). Elle couvre
  `deputes_2018`. Le calendrier `assemblee_nationale` du modèle suit le
  tableau de l'article 21 à la ligne près.
- *Mayotte.* Le décret n° 87-175 (1987-2002), l'ordonnance n° 2002-411 et le
  décret n° 2003-589 (2003-2017, puis à la génération depuis 2018), et
  l'extension du code de la sécurité sociale au 1er janvier 2028 (ordonnance
  n° 2026-647, L. 759-1 et L. 759-22). Les non-salariés, affiliés à la même
  caisse depuis 2012, restent sans statut, comme l'inventaire le disait.
- *Ce que le modèle ne fait pas*, et que les fiches nomment :
  1. **Navigants : la majoration temporaire.** De cinquante-cinq ans à l'âge
     légal, 0,8 % du plafond mensuel par annuité, vingt-cinq au plus — 20 % du
     plafond, près de 9 600 € par an en 2026 —, doublée de soixante-deux ans à
     l'âge légal depuis novembre 2023 ; ni elle, ni la majoration de trois
     enfants, ni le minimum de 795 € par annuité, ni la prestation de
     R. 6527-46-1 ne sont portés. Et le salaire moyen est celui de la carrière
     entière, non des vingt-cinq meilleures annuités.
  2. **Navigants : 111 % en 2024 et 2025.** Le taux d'appel est écrit (R. 426-8
     dans la rédaction du décret n° 2021-570, D. 6527-15) ; la fiche de régime
     garde 105 % jusqu'en 2025, et sa ligne d'inventaire le disait non publié.
  3. **Députés : la part de l'Assemblée.** « La subvention inscrite dans la
     Dotation égale au double des retenues » (article 2, 4°) : la fiche de régime
     la disait non écrite et ne porte que la retenue ; la cotisation simulée est
     le tiers de l'effort réel. Ni la bonification de deux trimestres par enfant
     né pendant le mandat d'une députée, ni l'arrondi au trimestre supérieur.
  4. **Mayotte, de 1987 à 2002 : la formule du décret.** 1,5 % par année des
     cinq meilleures années, 150 trimestres au plus, sans minoration, et un
     minimum de 22,5 % du SMIG ; la fiche de régime, qui la disait absente de
     l'index, prête celle du régime général.
  5. **Mayotte, de 2018 à 2027 : seize à vingt-quatre années.** Le salaire
     moyen des générations 1956 à 1964 se calcule sur moins de vingt-cinq ans.
     Et au 1er janvier 2028 le régime se fond dans le code de la sécurité
     sociale, que la fiche de régime prolonge.
  Les lignes d'inventaire des quatre régimes sont corrigées en conséquence ;
  les périodes, non. Au propriétaire de dire si ces cinq écarts ouvrent une
  action, avec les cinq de la note du 13 octobre.
- *Les tests.* `test_carte.py`, `test_textes.py`, `test_donnees.py` et la
  suite rapide passent ; le cliquet des textes reste à 9 773, les articles du
  code des transports et du décret n° 87-175 n'étant pas sur la liste.
  `docs/regimes.md` et `inventaire.yaml` sont refaits par leurs scripts.
- *Ce qui devrait s'écrire dans les pages*, pour la session qui les tient :
  rien en dur ; la page Données lit les lignes d'inventaire corrigées.
- *Ce qui reste de l'étape 2.* L'outre-mer du Pacifique et de
  Saint-Pierre-et-Miquelon : la CPS de Saint-Pierre-et-Miquelon (loi
  n° 87-563, dans l'index), la CAFAT, les deux tranches de la CPS de
  Polynésie, Wallis-et-Futuna, les fonctionnaires du Pacifique, dont les textes
  sont pour l'essentiel des délibérations locales hors de l'index ; puis les
  hors champ (CRFM de Mayotte, élus du Pacifique, régies ferroviaires
  d'outre-mer) ; puis les limites de l'étape
  (`docs/limites/4-regimes-incomplets.md`), une fois, à sa fin.
