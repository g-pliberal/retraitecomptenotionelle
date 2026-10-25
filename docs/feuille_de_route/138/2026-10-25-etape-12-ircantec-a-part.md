# Étape 12, quinzième partie : l'Ircantec aux pages, dite à part de la base — réduite avec elle jusqu'en 2020, entière depuis 2021

**Le 25 octobre 2026, la demande.** Vingt et unième vague du lot du 24 octobre,
une session par tâche, que le propriétaire a demandé de mener sans lui :
celle-ci, le point 1 du « Ce qui reste » de la note des phrases du cumul
(`…-phrases-du-cumul.md`), l'Ircantec que la page comptait encore avec la base.
Le site seul : aucune règle ne change, ni le moteur.

**Ce que la page disait.** `cumulEmploiRetraite` rangeait l'allocation de
l'Ircantec dans la base. La contractuelle partie en 2020
(`cumul_contractuelle_ircantec_2020`) lisait, sur toute son activité, « chaque
pension de base est réduite du dépassement, 1 131 € par mois en moyenne » : sa
base et son allocation ensemble, quand l'allocation, réduite du dépassement
d'août à décembre 2020, lui est servie entière depuis 2021
(`sans_le_troisieme_alinea`), ce que la page taisait.

**Ce qui est fait** (`moteur/js/pages.js`).

- *L'Ircantec, à part.* L'ensemble des complémentaires que la page dit à part de
  la base (`COMPLEMENTAIRES_A_PART`, naguère `COMPLEMENTAIRES_DU_NON_SALARIE`)
  compte l'allocation de l'Ircantec avec le RCI et les sections. La phrase de
  son sort (`sortDeLaComplementaireAPart`) dit, de 2004 à 2020
  (`l_161_22_2004`), qu'elle « l'est aussi », réduite du dépassement, comme le
  RCI depuis juillet 2024 ; depuis 2021, qu'elle « vous est servie entière : le
  règlement de l'Ircantec ne lui applique plus l'alinéa de L. 161-22 qui réduit
  chaque pension du dépassement ». Janvier 2021 coupe l'activité en deux.
- *Test* : un dans `tests/test_web.py`, sur la carrière du témoin au profil de
  son cas de base, comme les autres tests du cumul, posé sur l'article 14 de
  l'arrêté du 30 décembre 1970 et la note du 24 octobre, les montants pris aux
  tranches du modèle Python ; vu rouge, une seule phrase, de la somme.

**Mesuré.** Aucun témoin ne bouge, de page ni de simulation. La contractuelle
du témoin lit deux périodes : d'août à décembre 2020, 988 € de base et 494 €
d'allocation par mois, toute son allocation ; de janvier 2021 à janvier 2022,
996 € de base, l'allocation entière. La page dit de même l'Ircantec dans ses
autres états, vus au rendu, sans test à eux : suspendue avec la base de 2004 à
2014, elle « l'est aussi, pour la même durée » ; pour une première pension de
2027, les phrases du RCI, ce que la base n'absorbe pas ; avant 2004,
l'allocation, servie entière faute de règle lue (`servie_entiere_avant_2004`),
se tait comme le RCI d'avant 2009, et la base dit sa propre règle, « seul le
retour chez le dernier employeur privait de la pension », là où la page disait,
par l'allocation, la règle de la base « pas encore lue ».

**Ce qui reste.** Les restes du bloc : la veille du projet de loi de
financement pour 2027 ; au propriétaire, le RCO et le NRCO d'avant 2009
(action 89) et la part de base de l'ordre de D. 133-4 de 2016 à 2019.
