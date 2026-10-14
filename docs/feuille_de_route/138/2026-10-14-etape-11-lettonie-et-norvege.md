# Étape 11, troisième partie : la table G de la Lettonie et la grille publiée de NAV, rejouées

**La demande.** Le propriétaire, le 14 octobre 2026 : « action 138, étape 11 :
la Lettonie, puis la grille publiée des diviseurs, rejouées comme les exemples
de la Finlande et de la Pologne cette nuit, et gardées en cas d'essai ; un
écart se comprend avant de se corriger. » Le terme des versements, la
réversion dans le diviseur et ce que reçoit une année sans montant restent au
propriétaire : rien n'y est touché. La grille publiée est celle de NAV, le
point norvégien du registre (chantier 138.11, `delingstall_norvege`).

**Ce que les sources publient, lu le jour même.**

- *Lettonie* : la table G de la VSAA du 1er janvier 2026, de 40 à 90 ans
  (17,76 à 65 ans) ; la loi sur les pensions d'État, art. 13 (le Conseil des
  ministres fixe G sur les données du CSB) ; au portail du CSB, la table
  IRP030 de 2024, « pensijas aprēķinam », que G recopie nombre pour nombre, et
  la table abrégée IRP020 de 2024 (survivants et quotients aux âges ronds).
- *Norvège* : `Delingstall.xlsx` de NAV, publié le 26 juin 2026 (générations
  1954 à 1965, de 62 ans à 75 ans, mois par mois) ; le vedlegg du chapitre 4
  du forskrift 2009-12-22-1810, formules (1a), (1b), (2), (3) et (4) ; la
  table 07902 de SSB, « Begge kjønn », quotients en pour mille de 1980 à
  2025. Lovdata refuse les requêtes automatiques : le vedlegg a été lu par
  l'outil de lecture web.

**Ce qui est fait**, dans `tests/test_diviseur_exemples_officiels.py`, de la
suite rapide, par les deux moteurs (`diviseur_de_courbe`, `diviseurDeCourbe`) :

- *Lettonie.* La table G n'est pas une espérance de génération, comme le
  disait le registre d'après la fiche de l'Ageing Report (qui décrit la
  projection), mais l'espérance du moment de 2024, deux sexes. Sans
  actualisation, le diviseur du dépôt la refait au centième aux âges ronds
  de 40 à 85 ans, sur la table abrégée, la mortalité constante entre deux âges
  publiés, l'intervalle ouvert de 90 ans clos par G elle-même (4,05). Entre
  deux âges ronds, G interpole l'espérance en ligne droite, au centième.
- *Un écart compris avant d'être écrit.* La force de mortalité constante dans
  l'intervalle donnait au dépôt, aux âges intermédiaires, une espérance plus
  longue que G (0,035 an à 62 ans) ; une table par âge refaite des décès et
  des populations du CSB (IMV010, IRD041) montre au contraire une espérance
  convexe, que la ligne droite allonge de 0,02 à 0,04 an : l'écart venait de
  l'interpolation, non de la table. Il n'est pas gardé en essai ; celui que le
  registre déclare (G un peu trop long entre les âges ronds) tient.
- *Norvège.* La formule (4), écrite dans le test, refait au centième les 157
  nombres de la génération 1965 (20,41 à 62 ans), chaque mois en ligne droite
  entre deux âges entiers ; sur toutes les générations de 1954 à 1965, les
  1 884 nombres de la feuille l'étaient aussi, au brouillon (le test ne garde
  que 1965, pour sa taille). Le diviseur du dépôt, au taux 1/0,9925 − 1, en
  diffère de deux façons, exactement : l'escompte au milieu de l'année et non
  à son début (0,9925^½) ; le gain d'héritage, survie à l'âge de départ sur
  survie moyenne de 27 à 66 ans (0,964 à 62 ans, 0,827 à 75), qui reste
  `a_trancher`.
- *Le registre* : le point letton passe à `repris`, son « de génération »
  corrigé, au point comme au bilan ; le point norvégien de la grille garde
  `a_reprendre`, la grille de NAV refaite, celle du dépôt restant à publier.

**Ce qui reste**, dans l'ordre :

1. *Au propriétaire* (inchangé) : le terme des versements, la réversion dans
   le diviseur, ce que reçoit une année sans montant ni points ; le gain
   d'héritage norvégien.
2. *La grille du dépôt*, à publier : au modèle, une grille des diviseurs par
   génération et par âge ; à la session du site, sa page.
3. *Les autres parties de l'étape*, au registre, chantier 138.11 : le lissage
   italien exact, le lissage du seul réel, le prorata des mois de l'année du
   départ, les chocs stylisés du COR.
