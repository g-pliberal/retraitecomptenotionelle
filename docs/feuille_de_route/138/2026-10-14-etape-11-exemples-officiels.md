# Étape 11, deuxième partie : le diviseur éprouvé sur les exemples officiels de la Suède, de la Finlande, de l'Italie et de la Pologne

**La demande.** Le propriétaire, pour la nuit du 14 octobre 2026 : « action
138, étape 11, le diviseur éprouvé sur les exemples officiels de la Suède, de
la Finlande, de l'Italie et de la Pologne : chaque exemple publié, lu à sa
source, rejoué par les deux moteurs et gardé en cas d'essai ; un écart se
comprend avant de se corriger. » C'est le rang moyen du classement par poids
(note du 9 octobre), et quatre points du registre, chantier 138.11, qui
notaient tous que la fiche du diviseur n'a « aucun exemple officiel ».

**Ce que les sources publient, lu le jour même.**

- *Finlande* : le mémo de l'ETK du 26 octobre 2023 (`eak2024.pdf`) donne la
  formule, les quotients de 62 à 99 ans (q100 = 1 000 ‰), et EAL2009 =
  16,778288, EAL2024 = 17,718722, au taux de 2 %.
- *Suède* : PFS 2026:2, décidée le 2 septembre 2026, en vigueur le 12
  octobre, grille de la génération 1960 de 62 à 110 ans (17,34 à 65 ans) ; la
  table SCB `LivslangdFemarigA`, « totalt », risques de 2020-2024, lue par
  l'API de SCB.
- *Italie* : la Nota tecnica du décret du 20 novembre 2024, tableau A (les
  quotients de 2023 par sexe, de 50 à 119 ans), formule de l'allegato tecnico
  (annuité annuelle d'avance au taux de 1,5 %, moins k = 0,4615), tableau C.2
  (le diviseur par sexe et par terme, de 57 à 71 ans).
- *Pologne* : le communiqué du président du GUS du 25 mars 2026 (222,7 mois
  à 65 ans), et la table D du GUS, « Tablica trwania życia dla obu płci
  łącznie w 2025 r. », publiée le 27 juillet 2026, qui en porte les quotients.

**Ce qui est fait.**

- *Le diviseur d'une courbe*, sorti de `Convertisseur.coefficient` dans les
  deux moteurs (`diviseur_de_courbe`, `diviseurDeCourbe`) : la même boucle, aux
  mêmes opérations, si bien que rien ne bouge ; il se donne désormais une
  courbe de survie quelconque.
- *Le cas d'essai* `tests/test_diviseur_exemples_officiels.py`, de la suite
  rapide : chaque table y est recopiée de sa source, donnée aux deux moteurs
  par un seul appel à node, et confrontée au chiffre publié.
  - Finlande : exact au millionième, coefficient 0,94692 compris. La formule
    de l'ETK est celle du dépôt.
  - Pologne : exact au dixième de mois, à sept âges du communiqué. Le GUS
    arrondit l'espérance au centième d'année avant de la multiplier par
    douze : sans cet arrondi, 222,76 mois donneraient 222,8. L'intervalle
    ouvert de 100 ans se clôt par T100/l100 de la table.
  - Suède : le diviseur du dépôt, rente continue, est plus court d'un
    vingt-quatrième d'année (17,298 contre 17,34). La formule suédoise —
    douze mensualités d'avance, survie linéaire dans l'année, 1,016 —,
    écrite dans le test, refait la grille au centième de 62 à 103 ans ; au-delà,
    elle lit une mortalité d'après 110 ans que SCB ne publie pas, et la PFS
    borne le diviseur à 1,00.
  - Italie : sur le seul terme de la pension directe (17,590 à 65 ans), le
    diviseur du dépôt est plus court de 0,5 − k = 0,0385 an, à 0,004 près
    (17,548) ; la formule italienne, écrite dans le test, refait les deux
    sexes et leur moyenne à six dix-millièmes, les quotients étant publiés à
    sept décimales. Le terme de la réversion (1,460) reste au point du
    registre qui le garde `a_trancher`.
- *Le registre* : les quatre points passent à `repris`, chacun avec sa
  vérification ; la fiche du diviseur nomme le cas d'essai et la fonction.

**Ce que les écarts disent.** Aucun n'est une erreur : deux conventions
coïncident avec celle du dépôt (Finlande, Pologne), deux tiennent au terme des
versements (Suède, d'avance ; Italie, d'avance avec treize mensualités). La
pension française se paie par mois à terme échu (R. 355-2 du code de la
sécurité sociale), et le diviseur exact serait l'annuité moins 13/24 d'année,
plus court encore d'environ 0,04 an, soit 0,2 % de pension. Ce n'est pas
corrigé : le README définit le diviseur comme « l'espérance de vie restante »,
que le dépôt calcule exactement, et le registre garde ce choix `a_trancher`
(point suédois des mensualités, point italien de k).

**Ce qui reste**, dans l'ordre :

1. *Au propriétaire* : le terme des versements dans le diviseur (rente
   continue, ou mensualités échues) ; la réversion tarifée dans le diviseur ;
   ce que reçoit une année sans montant ni points (première partie).
2. *La Lettonie* (table G du 1er janvier 2026, 17,76 à 65 ans), cinquième
   exemple du registre, hors de la demande de cette nuit : il s'ajoute au même
   cas d'essai.
3. *Les autres parties de l'étape*, au registre, chantier 138.11 : la grille
   publiée des diviseurs, le lissage italien exact, le lissage du seul réel,
   le prorata des mois de l'année du départ, les chocs stylisés du COR.
