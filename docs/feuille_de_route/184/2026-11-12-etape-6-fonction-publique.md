# Étape 6, lot « la fonction publique » : seize lectures, huit fiches, deux écarts relevés

**Le lot est fini le 12 novembre 2026.** Les huit fiches n'ont plus de
rédaction en vigueur ou à venir non lue
(`python scripts/textes.py --non-lues <fiche>` : zéro pour chacune). Le
cliquet passe de 9 283 à 9 274. Deux rédactions changent ce que le modèle
calcule ; elles ne sont pas portées, selon la consigne de l'étape, et
attendent la décision du propriétaire.

## Ce qui change une règle

1. **La pension militaire dans le cumul emploi-retraite de 2027.** L. 86 du
   code des pensions, rédaction du 31 décembre 2025 (LEGIARTI000053279638,
   loi n° 2025-1403, article 102), pour qui entre en jouissance de sa première
   pension de base à compter du 1er janvier 2027. Le code de la sécurité
   sociale laisse le titulaire d'une pension militaire cumuler entièrement
   (L. 161-22, III, C, 1° ; L. 161-22-1-2, 4°), et L. 86 ne le plafonne, « par
   dérogation » à ce C, que devant un employeur public : le tiers de la
   pension et la moitié du minimum garanti, sauf le non-officier de moins de
   vingt-cinq ans de services, la limite d'âge atteinte et l'invalidité. Le
   portage applique à toute pension de la fonction publique les trois régimes
   selon l'âge (`regle2027`, `moteur/js/droit/cumul.js`), sans regarder si
   elle est militaire : le sous-officier parti à quarante-cinq ans en 2027 et
   salarié du privé y perd une pension que le droit lui laisse entière. Lu
   dans le code, non rejoué. Le même C laisse aussi cumuler entièrement les
   pensions d'invalidité, civiles et militaires (L. 161-22-1-2, 5°) : ce que
   le modèle en fait reste à lire. Fiche
   `cumul_emploi_retraite_fonction_publique` : une approximation de plus sur
   la version `regles_communes_2027`, et la question dans `sources.a_relire`.
2. **Le début d'activité du non-salarié agricole en carrière longue.**
   D. 732-40 du code rural, rédaction du 1er janvier 2026
   (LEGIARTI000053365409, décret n° 2025-1410), pour les pensions prenant
   effet à compter de ce jour. Le non-salarié agricole est tenu pour entré
   avant la borne s'il a « validé au titre » de son régime « quatre
   trimestres à la fin de l'année » de l'anniversaire, quel que soit son mois
   de naissance. La rédaction du 1er septembre 2023 offrait déjà cette voie,
   à côté de celle de D. 351-1-3 ; celle de 2026 l'écrit « par dérogation » à
   D. 351-1-3. Le modèle demande cinq trimestres à tous, quatre au seul né du
   dernier trimestre (`entreePrecoce`, `moteur/js/regimes.js`) : l'exploitant
   installé au 1er janvier de l'année de ses dix-huit ans, né avant octobre,
   n'y a pas la porte que le texte lui ouvre. L'écart ne date donc pas de
   2026 ; c'est cette lecture qui le relève. Restent à lire avant de
   l'écrire : depuis quand la voie existe (rédactions de 2005, 2011 et 2012),
   si la rédaction de 2026 ferme au non-salarié agricole la voie des cinq
   trimestres tous régimes, et comment la MSA l'applique. Fiche
   `carriere_longue` : `textes_a_rattacher` et `sources.a_relire`.

**Une décision qui revient au propriétaire.** La fiche `carriere_longue`
reste `conforme` : l'écart ne touche qu'un régime sur les dix qu'elle couvre,
et un cas étroit. La passer à `approchee` déplacerait ce que le site dit de
toute carrière longue ; cette passe ne l'a pas fait.

## Ce qui change le droit sans toucher ce que le modèle sert

- L. 50 du code des pensions, rédaction du 1er janvier 2017
  (LEGIARTI000033814300) : un 9° au II, le militaire tué dans l'exercice de
  ses fonctions sur le territoire national, ou mort en service et cité ; au
  5°, la citation à l'ordre de l'armée. La fiche `reversion_fonction_publique`
  déclare déjà que la pension pour décès en service n'est pas portée :
  `textes_a_rattacher`.

## Les seize lectures

| Fiche | Rédaction | Statut donné |
|---|---|---|
| `militaires_duree_requise` | L. 13 du code des pensions, 31 décembre 2025 | lecture : sans effet sur elle, la durée tient au C du XXIV |
| `bonification_cinquieme_militaires` | L. 13, 31 décembre 2025 | lecture : sans effet sur elle, le maximum reste 75 % |
| `categorie_active_duree_requise` | L. 13, 31 décembre 2025 | lecture : sans effet sur elle, le B du XXIV déroge à L. 13 |
| | L. 161-17-3 du code de la sécurité sociale, 31 décembre 2025 | lecture : sans effet sur elle |
| | loi n° 2003-775, article 5, 1er janvier 2017 | `textes_sans_effet` : le VI inchangé |
| `duree_requise_carriere_longue_fonction_publique` | L. 13, 31 décembre 2025 | lecture : sans effet sur elle |
| | L. 25 bis, 31 décembre 2025 | lecture : la durée inchangée, le 4° à la fiche `carriere_longue_enfants_reputes_cotises` |
| `carriere_longue` | D. 16-1 du code des pensions, 1er septembre 2026 | lecture : les portes de D. 351-1-1 à la même date, ligne pour ligne, que le modèle ouvre déjà aux fonctionnaires |
| | D. 16-3, 1er septembre 2023 | lecture : le début d'activité de D. 351-1-3 |
| | L. 25 bis, 31 décembre 2025 | lecture : âges et durée inchangés |
| | décret n° 73-937, article 3 bis, 1er novembre 2012 | lecture : renvoie à D. 351-1-1 à D. 351-1-3 |
| | D. 732-40 du code rural, 1er janvier 2026 | `textes_a_rattacher` : voir plus haut |
| `cumul_emploi_retraite_fonction_publique` | L. 86, 31 décembre 2025 | `textes_a_rattacher` : voir plus haut |
| | L. 86-1, 31 décembre 2025 | `textes_sans_effet` : la liste des employeurs inchangée |
| `retraite_pour_invalidite_fonction_publique` | décret n° 2003-1306, article 37, 18 avril 2024 | `textes_sans_effet` : renvoi au code général de la fonction publique |
| `reversion_fonction_publique` | L. 50, 1er janvier 2017 | `textes_a_rattacher` : voir plus haut |

Chaque rédaction a été lue dans l'index LEGI à jour au 11 novembre 2026, et
comparée mot à mot à la précédente ; pour L. 13, L. 25 bis, L. 86, D. 16-1 et
D. 732-40, les deux versions ont été lues en entier. La table des portes de
septembre 2026 (`legislation/carriere_longue.csv`) a été comparée ligne à
ligne au tableau de D. 16-1.

## Deux choix de méthode, à connaître des autres lots

- **Une lecture plutôt que `textes_sans_effet`, quand la rédaction fonde une
  règle ailleurs.** Le statut d'une rédaction est le plus établi que les
  fiches lui donnent : dès qu'une fiche la déclare sans effet, elle sort de
  la liste des non-lues de toutes les autres
  (`noyau/textes.py`, `non_lues`). L. 13 du 31 décembre 2025 est aussi à lire
  par `taux_plein_a_soixante_cinq_ans`, d'un autre lot ; L. 161-17-3, L. 25 bis
  et D. 16-1 fondent des règles que d'autres fiches portent. Les déclarer sans
  effet ici les aurait dites sans effet partout. Elles sont donc citées dans
  une lecture, qui dit pourquoi la fiche n'en bouge pas, et gardent le statut
  « à rattacher ». `textes_sans_effet` n'a servi qu'aux retouches de forme.
- **`sources.lu_le` passe au 12 novembre** sur les huit fiches, comme l'étape
  le demande ; il dit ici que leurs rédactions en vigueur sont lues, non que
  leurs autres sources l'ont été. `prochaine_relecture` n'a pas bougé.

## Le cliquet

Neuf rédactions sortent du compte des sans-statut : huit des douze du lot,
les quatre autres ayant déjà un statut par une autre fiche ou par
l'inscription, et L. 13 dans sa rédaction du 1er septembre 2023
(LEGIARTI000047452824), lue en entier pour la comparer et citée à ce titre.
La fiche du cumul cite aussi L. 161-22 et L. 161-22-1-2 du code de la
sécurité sociale, rédactions du 31 décembre 2025, lus pour comprendre la
dérogation de L. 86 : elle suit donc désormais ces deux articles, que
d'autres fiches citaient déjà.

## Ce qui reste

Les rédactions passées, que cette passe ne lit pas : 100 pour les huit
fiches (`--non-lues <fiche> --toutes`). Aucune rédaction en vigueur.
