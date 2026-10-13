# Étape 6, le financement et le coût : le jaune 2027 confronté à ce que la page Coût lit, deux corrections et deux écarts déclarés

Les tableaux que l'étape 0 rangeait à l'étape 6 ont été relus dans le jaune
annexé au PLF 2027 (`data/brut/34465.pdf`, tiré de la branche `jaune-2027`,
empreinte vérifiée ; `pdftotext -layout`, page par page), et confrontés à ce
que la page Coût lit : `donnees/cotisants.py`, `donnees/financement_regimes.py`
et les comptes du COR que `cout.py` charge. Presque tout recoupe, et deux tests
le tiennent désormais. Deux corrections, deux mises à jour, deux écarts
déclarés, chacun dans son commit ; le document se contredit en six endroits,
qui ne changent rien au dépôt.

## Ce qui change

- **La clé civils-militaires de l'État** (tableau D-5). Le COR ne publie les
  cotisants de l'État que d'un seul tenant ; la page Coût les partage entre le
  sédentaire et le militaire à la clé du jaune, tenue constante. Elle passe des
  1,63 et 0,32 million du jaune 2026 aux 1 584 758 civils et 321 432 militaires
  du 31 décembre 2025 (`COTISANTS_ETAT_2025`) : un militaire pour 4,93 civils
  au lieu de 5,09. Du côté de la recette, le militaire pèse 2,8 % de plus, le
  sédentaire 0,5 % de moins. Aucun chiffre ancré de la prose n'en bouge :
  `verifier_prose.py`, passé avant et après sur deux empreintes du modèle,
  rend les mêmes valeurs. La clé glisse vite — 5,82 civils par militaire en
  2016, première année où les deux versants comptent leurs comptes
  individuels actifs —, mais rien ne dit comment elle évoluera : elle reste
  constante, et le docstring le dit.
- **Les cotisants du FSPOEIE, mille fois trop peu.** La feuille du FSPOEIE du
  classeur du COR écrit « Effectifs de cotisants en milliers » au-dessus de
  0,0173 pour 2024 : des millions. `cotisants.csv` comptait donc 17 cotisants
  en 2024 et 0 dès 2062 ; il en compte 17 349 en 2024 et 61 en 2070, que le
  tableau D-5 bis recoupe (17 144 au 31 décembre 2023, 16 079 un an plus tard).
  Ses retraités, annoncés en milliers eux aussi, l'étaient bien.
  `verifier_donnees.py` redresse l'unité de cette seule feuille
  (`UNITE_COTISANTS_CORRIGEE`), et la série a été recertifiée seule, journal
  compris : 47 années corrigées, aucune autre. Aucun cas type ne porte les
  effectifs du FSPOEIE : aucun résultat ne bouge, seul le paquet du site.
- **Le recoupement de la majoration pour enfants** (`test_avantages.py`), que
  la note de l'étape 2 renvoyait ici : stock de fin 2025 (A-7), part et
  supplément moyen du flux de 2025 (B-1). La fonction publique en porterait
  2,21 Md€, 28 % du poste des comptes de 2024, le dernier qu'ils publient ;
  2,15 Md€ et la même part avec le jaune 2026.
- **Les engagements de l'État** (tableaux 10 et 11), dans le référent `pablo` :
  1 366 Md€ fin 2025 au taux réel de 2,21 % (OAT€i 2047), de 1 265 à
  2 018 Md€ entre 2,71 % et 0 %, dont 798 pour les retraités ; 1 565 Md€ au
  taux de 1,38 % de l'an passé, contre 1 573 fin 2024 ; 31,3 Md€ pour les
  ouvriers de l'État. Les numéros de ligne de `cout.py` que la fiche citait,
  périmés, cèdent aux noms : `calculer_engagements`, `EngagementAcquis`,
  `ECARTS_ACTUALISATION`. Le dépôt n'a toujours aucun engagement par régime :
  le compte général de l'État ne peut pas servir de repère à la page Coût, et
  le chantier 138.3 garde la question.

## Ce qui recoupe, et que deux tests tiennent

`test_ce_que_l_etat_verse_recoupe_le_jaune_pensions_2027` et
`test_les_cotisants_du_cor_recoupent_le_jaune_pensions_2027`, dans
`test_donnees.py`, avec les chiffres du jaune saisis, comme le recoupement de
la majoration.

- **Les subventions d'équilibre de 2025** : 6 009 M€ aux régimes spéciaux
  (tableau 5) et 1 653,8 M€ aux ouvriers de l'État (tableau 23), 7 663 M€ ;
  les comptes du COR que la page lit en donnent 7 592 (1,82 % de ressources de
  417 Md€). C'est le poste que le scénario 6 ne reconduit pas.
- **La contribution d'équilibre de l'État de 2025** : 48 006 M€
  d'État-employeur au programme 741 (tableau D-3), 48 708 chez le COR. Le
  poste du système est donc la contribution de l'État lui-même.
- **La part de l'État, régime par régime** : celle du classeur du COR de 2023
  (`structure_financement.csv`) contre la subvention de 2025 rapportée aux
  dépenses — SNCF 60,8 contre 58,4 %, RATP 60,8 contre 62,2, marins 76,3
  contre 74,9, mines 81,1 contre 80,6, ouvriers de l'État 76,7 contre 78,6.
  La bascule de 2025, où la CNAV équilibre les régimes fermés et l'État la
  compense, n'a pas déplacé ces parts, et le jaune compte encore ces crédits
  en subventions.
- **Les cotisants de 2024** : la moyenne annuelle du COR contre la moyenne des
  deux fins d'année du jaune (D-5, D-5 bis) — l'État 3,7 % au-dessus, le COR
  comptant des cotisants distincts et le jaune des comptes individuels actifs,
  la CNRACL 1,0 %, le FSPOEIE 4,4 %. Le test aurait vu les dix-sept cotisants.
- **Les ratios démographiques** (tableaux 113 à 115) sont ceux de l'exercice
  du COR de juin 2024, le millésime du classeur du dépôt : le rapport brut de
  ses séries, cotisants sur retraités de droit direct, vaut 1,0 à l'État de
  2024 à 2060 (0,9 corrigé dans le jaune, qui compte la moitié des droits
  dérivés) et descend à la CNRACL de 1,58 à 0,99 en 2070 (de 1,5 à 0,9
  corrigé). Même profil ; rien à écrire.
- **Le CAS Pensions** (graphiques 17 et 18, tableau 19, D-3) : les pensions de
  2025, 53 897 M€ de civiles et 11 108 de militaires, sont à 0,2 % des
  prévisions du PAP 2026 (`pap_regimes_subventionnes.csv`). Le solde cumulé
  du compte fond, de 9 490 M€ fin 2021 à 2 600 fin 2025, ce qui explique les
  quatre points de taux civil de 2025 et de 2026 que l'étape 3 a recoupés.

## Ce qui se déclare

- **Les 86 % « de l'État » sont ceux de tous ses employeurs.** Le classeur du
  COR range sous `contribution_equilibre_etat` 86,0 % des ressources du régime
  de l'État en 2023 ; le tableau D-3 en rend 85,8 % à tous les employeurs, dont
  74,3 points à l'État-employeur, 10,6 à ses établissements publics et autres
  employeurs, 0,8 à La Poste et Orange (et 12,3 % aux retenues, 12,2 chez le
  COR). Au niveau du système, le même mot désigne la seule contribution de
  l'État : les deux fichiers du COR ne l'entendent pas pareil. `part_etat`
  garde la convention du classeur, et le dit ; le docstring de
  `financement_regimes.py`, celui de `simulateur.financement_regimes` et les
  deux en-têtes de `structure_financement.csv` ne prêtent plus les 86 % à
  l'État seul. Aucun calcul ne lit `part_etat` aujourd'hui.
- **La subvention d'équilibre du FSPOEIE**, que l'étape 3 renvoyait ici : la
  série de taux du FSPOEIE, certifiée depuis 2000, laisse dehors, comme celles
  des autres régimes spéciaux, les 1 653,8 M€ que l'État verse en 2025, 81 %
  des prestations du régime (2 042,7 M€) et 5,7 fois ses cotisations
  (289,4 M€). `docs/limites/4-regimes-incomplets.md` le dit avec la SNCF.

## Ce qui ne se compare pas

- **La CNRACL** (tableaux 20, 21, 116, D-4) : un résultat de −2 342 M€ en
  2025, des réserves de −10 225 M€, 2 145 845 cotisants pour 1 668 446
  pensionnés. Le classeur du COR lui donne 7,1 % de besoin de financement en
  2023, quand le D-4 dit −2 523 M€ de résultat sur 25 119 M€ de produits : un
  solde technique contre un résultat comptable, qui porte en plus la
  compensation versée et des charges financières. Le tableau 116, le solde
  technique du COR de juin 2024 (−0,1 % du PIB en 2024), est le même ordre de
  grandeur. Rien à corriger.
- **La dépense de l'État chez la DREES** (`depenses_retraite_regimes.csv`) :
  64 650 M€ en 2024, 1,7 % de plus que les 63 598 M€ du tableau D-1, au
  périmètre de la comptabilité nationale, que le jaune ne détaille pas. Noté,
  sans suite.

## Ce que le document dit contre lui-même

- Le titre de la figure 1 écrit « 4130 Md€ » pour les 413 Md€ de la branche
  vieillesse, et la page 17 « 99, Md€ » pour les quatre régimes dédiés.
- Le texte de la page 37 donne 314,3 Md€ d'engagements pour les ouvriers de
  l'État, que le titre et le tableau 11 disent 31,3.
- Le tableau D-5 imprime « 1 » pour le total des pensionnés militaires de
  2025, et une évolution de −100 %.
- Le tableau 21 donne 27 682 M€ de cotisations à la CNRACL en 2025, le D-4
  27 582,2 ; le texte de la page 57 suit le premier (27,7 Md€, +7,5 %).
- La page 31 écrit un ratio démographique corrigé de 1,29 pour la CNRACL en
  2025, que le tableau 20 et le D-5 bis disent 1,37.
- La note du tableau 115 définit le ratio corrigé à l'envers de celle du
  tableau 113, retraités sur cotisants.

## Ce qui va aux autres étapes

- **Étape 8, le site** : le poids des pensions dans le budget général, 11,4 %
  en 2025 (D-1, figures 8 et 9), avec la part de chaque ministère. La phrase de
  la page Coût sur la clé du jaune, « tenue constante », reste vraie.
- **Action 129** : le jaune confirme que la contribution d'équilibre du
  système chez le COR est celle de l'État-employeur (48,7 contre 48,0 Md€ en
  2025), quand le poste du même nom, régime par régime, compte tous les
  employeurs.

*Ce qui reste.* Rien pour l'étape 6. GitHub refera le paquet et les fichiers
fabriqués que la clé et les cotisants du FSPOEIE déplacent.
