# Le sixième domaine, étape 4 : les exemples des circulaires, rejoués dans les deux moteurs

Session 3 de la vague quater du 16 octobre 2026, sans le propriétaire. L'étape 4
du gabarit (`2026-10-14-sixieme-domaine-mesure.md`) : les exemples que la Cnav
publie sur l'apprentissage et les stages, lus à leur source et rejoués dans les
deux moteurs. Aucun fichier du modèle ne bouge, ni aucun témoin.

## Ce qui est fait

- **Les deux circulaires, relues dans leur texte** : la 2016-41 du 17 octobre
  2016 (annexe, exemples 1 à 4) et la 2024-18 du 11 avril 2024 (point 3.2.2,
  exemples 1 à 4), téléchargées de la base documentaire de la Cnav.
- **Le cas d'essai** `tests/test_periodes_assimilees_exemples_officiels.py`, de
  la suite rapide : chaque exemple recopié à ses dates et à ses euros, en
  chronologie — l'apprenti par un relevé dont les lignes du contrat portent
  l'attribut, le stagiaire par ses périodes déclarées —, compté par les deux
  moteurs en un seul appel à node (`tests/js/comparer-assimilees.mjs`), et
  confronté aux trimestres que la circulaire publie.
  - *2016-41* : les trimestres garantis des trois premiers contrats, 1, 4 et 3,
    puis 0, 4 et 1 ; l'exemple 4, payé 1 110, 4 950 et 4 860 euros, valide 0, 3
    et 3 trimestres par ses salaires, et le complément porte l'année à 1, 4 et
    3, « 0 cotisé et 1 complémentaire », « 3 et 1 », « 3 et 0 ».
  - *2024-18* : 87 jours, un trimestre ; 46 et 34 jours, un ; le stage
    d'octobre 2014 à mars 2015, rien en 2014, « dispositif non entré en
    vigueur », un en 2015 ; toute l'année 2015 à 3 220 euros d'assiette, deux
    trimestres de salaire et sept assimilés « ramenés à 2 », quatre en tout.
- **Les fiches** `apprentissage` et `stages_formation_professionnelle` nomment
  le cas d'essai ; leur champ `exemples` reste « aucun trouvé », puisqu'il ne
  reçoit que des identifiants de `exemples_officiels.yaml`, que l'oracle
  rejoue sur une carrière minuscule sans période assimilée.

## Ce que les exemples apprennent

Aucun écart du modèle. Deux fautes de plume des circulaires, sans effet sur
leur résultat : le contrat de l'exemple 3 de la 2016-41 finit le 14 février
2016, non 2015, comme son décompte le suppose ; l'exemple 1 de la 2024-18
compte « 88 jours » du 1er janvier au 28 mars, que le calendrier compte 87, et
la chronologie refuse plus de jours qu'une période n'en a : il se rejoue sur
ses dates.

## Ce que l'étape laisse aux suivantes

- **Étape 5**, la saisie, à la session des pages, inchangée.
- **Étape 6**, la page Coût : le complément de l'apprentissage, que le FSV puis
  la branche versent, n'est isolé dans aucune publication lue.
- **Étape 7**, la décision de la proposition.
- Les exemples pourraient entrer à `exemples_officiels.yaml` le jour où
  l'oracle saura déclarer un contrat d'apprentissage et une période assimilée
  dans sa carrière minuscule ; le cas d'essai les tient d'ici là.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition, à l'étape 7.
