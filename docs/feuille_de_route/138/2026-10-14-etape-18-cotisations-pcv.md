# Étape 18, deuxième partie : les cotisations PCV (ex-ASV) des professions de santé conventionnées

**La demande.** Session de nuit du 14 octobre 2026, tâche n° 5 : « action 138,
étape 18, les cotisations PCV (ex-ASV) des professions de santé conventionnées,
[…] les deux côtés, la pension du scénario 1 et le compte, dans les deux
moteurs, texte en main. Si la règle demande le secteur ou la convention du
professionnel, que la saisie ignore, présume-les et déclare la présomption. »
Ni `pages.js`, ni les pages, ni la saisie n'ont été touchés ; aucun fichier n'a
été déplacé.

**Ce que disent les textes**, lus dans l'index LEGI à jour du 13 octobre, et
au guide de l'assurance vieillesse des professions libérales de la CNAVPL,
édition 2025, p. 84 à 96.

- *La part des caisses.* L. 645-2 et L. 645-3 font payer une partie de la
  cotisation par l'assurance maladie ; D. 645-3 la fixe au double de celle du
  professionnel de 1985 à 2004, sauf pour les médecins du 30 mars 1993 au
  8 juillet 1994, où elle lui est égale. En 2025 : les deux tiers du forfait et
  de l'ajustement du médecin de secteur 1 (1 852 € et 1,2667 % pour lui, sur
  5 556 € et 3,80 %), rien en secteur 2 ; les deux tiers du forfait et 60 % de
  l'ajustement de l'auxiliaire médical (222 € et 0,16 %, sur 665 € et 0,40 %) ;
  les deux tiers du forfait et la moitié de l'ajustement du chirurgien-dentiste
  (1 648,76 € et 0,725 %, sur 4 946,28 € et 1,45 %) ; les deux tiers des 780 €
  de la sage-femme.
- *L'auxiliaire médical* (décret n° 2008-1044). Un forfait total de 400 € en
  2008, 500 € en 2009 et 2010, 540 € en 2011, puis revalorisé sur les prix,
  qui ouvre 44, 26,5, puis 24,5 points ; un ajustement de 0,25 % en 2010 et
  0,40 % depuis, dont les points sont le rapport de la cotisation totale,
  multipliée par les points du forfait, au forfait, « arrondi au dixième
  supérieur » ; 1,49 € le point acquis depuis 2006, en 2025. La retraite à
  65 ans, ou dès 60 avec un coefficient de 0,75 à 0,95.
- *Le chirurgien-dentiste* (décret n° 2007-458). Un forfait total de 3 150 € en
  2007, 3 600 € en 2008, 3 900 € en 2009, puis revalorisé sur les prix, qui
  ouvre dix points ; un ajustement de 0,75 % de 2008 à 2017, 1,10 % en 2018,
  1,45 % depuis, qui ouvre au plafond de cinq plafonds un point, 1,47, puis
  1,93, au prorata en deçà ; 28,5747 € le point en 2025. Le taux plein à
  67 ans, la minoration de 1,25 % par trimestre bornée à 15 %, 10 % de plus
  pour trois enfants.
- *Avant ces décrets*, les cotisations et les points s'exprimaient en lettres
  clés, dans des articles que l'index ne garde pas ; aucune source trouvée ne
  dit le nombre de points d'une année. Aucun exemple chiffré publié n'a été
  trouvé.

**Ce qui est fait**, en un envoi (5107624).

1. *Les deux moteurs.* Trois champs de période : `part_assurance_maladie_forfait`
   et `part_assurance_maladie_taux`, les fractions du total que paient les
   caisses, et `points_ajustement_au_plafond`. `PeriodeRegime.prise_en_charge`
   et `ajustement_total` (jumelles `priseEnCharge`, `ajustementTotal`) en
   tirent ce que versent les caisses et le rapport des cotisations totales. Le
   compte porte la part des caisses comme une part patronale, sous les
   conventions qui portent celle-ci (scénarios 4 et 5) ; le scénario 1 compte
   les points d'ajustement sur la cotisation totale, et ceux du dentiste au
   plafond. Le paquet garde sa version : les champs ne s'écrivent que là où ils
   servent.
2. *Les médecins.* La part des caisses dans les vingt-deux périodes
   d'`asv_conventionnes` (la moitié en 1993 et 1994) ; le forfait de 2025 et de
   2026, 1 852 et 1 917 €, au lieu de celui de 2016 projeté sur les prix. Leurs
   points ne changent pas.
3. *Deux fiches neuves*, `asv_auxiliaires_medicaux` (depuis 1975, statut
   `auxiliaire_medical`, ses âges dans `ages_regimes.csv`, table
   `pcv_auxiliaires_medicaux`) et `asv_chirurgiens_dentistes` (depuis 1978,
   statut `chirurgien_dentiste_ou_sage_femme`), avec leurs pivots et leurs
   réformes. `tests/test_pcv_sante.py` les tient, avec la part des caisses et
   l'accord des deux moteurs.

**Les présomptions**, chacune déclarée dans sa fiche.

- Le médecin est en secteur 1 ; en secteur 2, il paie tout et les caisses
  rien : son compte sous la convention salariale est trois fois trop bas, sous
  la convention totale juste.
- Le statut `chirurgien_dentiste_ou_sage_femme` est un chirurgien-dentiste,
  comme pour sa complémentaire : la sage-femme reçoit ainsi près de trois fois
  ses PCV (18 points par an à 6,10 €).
- L'auxiliaire et le dentiste sont conventionnés.
- Avant 2008 et 2007, la règle permanente du décret : 24,5 points par an pour
  l'auxiliaire, dix pour le dentiste, sans ajustement, et le forfait de 2008
  et de 2007 projeté en arrière sur les prix ; ces points valent celui d'après
  2006, quand le texte leur donne une valeur par tranche d'années.
- Le partage avec les caisses lu pour 2025 vaut à toutes les années.
- Ni l'arrondi des points d'ajustement, ni l'assiette de l'avant-dernière
  année, ni la borne de 420 points du dentiste jusqu'en 2021.

**Ce que montrent les mesures**, pour une assurée née en 1960, au salaire moyen
de 25 à 65 ans.

- *L'infirmière* reçoit 1 642 € de PCV par an (1 102 points à 1,49 €), un
  dixième de sa pension ; 1 792 € à deux fois le salaire moyen.
- *La chirurgienne-dentiste*, 10 576 € (406 points à 28,57 €, minorés de
  8,75 % à 65 ans), plus du tiers de sa pension.
- *La médecin* garde ses points.
- *Le compte*, sous la convention totale : les caisses font 6 à 8 % de ce que
  reçoit celui de l'auxiliaire, 19 à 27 % de celui du dentiste, 17 à 21 % de
  celui du médecin. Sous la convention salariale, rien ne change pour le
  médecin ; l'auxiliaire et le dentiste y gagnent leur propre part.

**Pour les pages**, que la session du site tient.

- La saisie pourrait demander la profession sous le statut de la CARCDSF
  (dentiste ou sage-femme) et sous celui du pharmacien (biologiste ou non),
  et le secteur du médecin : trois présomptions tomberaient.
- Le détail de la pension nomme les deux régimes neufs par leur nom de fiche ;
  les témoins de pages que GitHub refera montreront ces lignes pour les
  statuts de la santé, et un compte plus gros sous les scénarios 4 et 5.

**Ce qui reste** du point, au propriétaire ou à une session de données : les
points d'avant 2007 et 2008, au Bulletin officiel ou dans les statuts des deux
sections ; les forfaits des médecins de 2017 à 2024, que la CARMF publie ; les
règlements des sections approuvés par l'arrêté du 10 juillet 2026 ; la
sage-femme et le directeur de laboratoire, quand la saisie les distinguera ; un
exemple chiffré à rejouer. Le reste de l'étape est au bloc « Reprise » de la
première partie.
