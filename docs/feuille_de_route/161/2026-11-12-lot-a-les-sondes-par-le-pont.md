# Lot A, seconde ligne : les sondes de la prose et les mesures de l'accueil par le pont

**Ce qui est fait.** `scripts/mesures_prose.py`, que `verifier_prose.py`
lance à chaque envoi, et `scripts/mesures_accueil.py` n'entrent plus dans le
moteur Python d'une carrière. Leurs carrières se bâtissent et se simulent au
portage, et les règles qu'elles appelaient une à une s'y appellent par
`pont.droit`, sous le nom de leur jumeau. Les chiffres n'ont pas bougé : les
508 mesures que la prose cite sont identiques au bit près, avant et après.

1. *La sonde voit ce qu'elle ne voyait pas.* `scripts/entrees_du_moteur.py`
   déclare portes les règles des fichiers mêlés que les sondes appelaient :
   `salaire_moyen_annuel`, cinq lectures de la fiche de paie
   (`remuneration.py`), `ActuelAujourdhui.pension_annuelle`, et deux méthodes
   de `Restitution`, qui part avec le moteur (note de décision 0007). Le
   relevé des onze étapes, refait sous ces portes, n'a montré aucune entrée
   de plus hors des sondes.
2. *Quatorze entrées au pont*, en un bloc à part de chaque côté
   (`FONCTIONS_DES_SONDES` dans `pont.mjs`, `LECTURES_DES_SONDES` dans
   `pont.py`, `JUMEAUX_DES_SONDES` dans `tests/outils_pont.py`), qui
   s'ajoutent aux fonctions du droit :

   | entrée du pont | les sondes qui la demandent |
   |---|---|
   | `simulateur.simuler` | `ecart`, `pension`, `aujourd_hui`, `part_employeur`, `part_salariale_versee`, `gain_net`, `fiche`, `indemnite_csg`, `avance`, `droits_acquis`, `droits_acquis_variation`, `fourchette` |
   | `indexation.coefficient` | `cumul_indexation`, `conserve`, `fois_prix`, `taux_indexation`, `composition_revalorisation` |
   | `fusion.fusionner`, `fusion.taux_total.tranche_1` | `fusion`, `taux_statut` ; `solde_fusion.hypotheses`, pour l'accueil |
   | `carriere.salaire_moyen_annuel` | `salaire_moyen`, `smic_annuel`, `millieme_salaire` |
   | `conversion.coefficient.esperance_residuelle`, `conversion.effet_anticipation` | `anticipation` |
   | `notionnel.garantie_vieillesse` | `garantie_complement`, `garantie_foyer` |
   | `capitalisation.construire`, `capitalisation.facteur_encours_rente` | `allocation`, `frais_reserve` |
   | `restitution.part_du_poste`, `restitution.annuelle.points_csg` | `restitution` |
   | `age_reference.age`, `compte.parts_retraite_seule` | `age_reference`, `retraite_seule` |

   `ecart_openfisca` passe par une entrée qui existait,
   `liquider.salaire_de_reference`. `simulateur.simuler` rend le résultat tel
   que les témoins l'écrivent (`Comparaison.dictionnaire()`), relu sous la
   table des types, et ce qu'il ne porte pas : le diviseur de chaque scénario
   et la fiche de paie de l'année de référence.
3. *Une variante écrite en données.* La sonde `allocation` remplaçait la
   règle d'allocation du pilier le temps d'un calcul
   (`capitalisation.repartition`), ce que le portage ne voit pas. Le
   constructeur du pilier reçoit maintenant une autre allocation en paramètre
   facultatif, des deux côtés (`repartir`), et la demande la décrit par
   horizon. Les tests de `test_capitalisation.py` qui échangent encore la
   fonction du module restent verts ; ils pourront passer par là.
   `fusion.js` exporte `tauxTotal`, que la fusion gardait pour elle.
4. *L'accueil.* `solde_fusion.hypotheses` reçoit le simulateur, non plus son
   catalogue : la fusion se demande au pont sous ses paramètres, les
   conventions de la page Coût comprises.
5. *Les deux exemples du README.* Le titre du second lit l'écart à l'âge de
   référence sur ce que le pont rend. Leur tableau reste écrit par
   `Comparaison.tableau()` : `construire_tableaux_md.py` bâtit et simule
   pour cela, lui-même, les deux carrières au moteur Python.

**Ce qui entre encore dans le moteur Python depuis la fabrique**
(`ENTREES_DE_LA_FABRIQUE`, de 28 appels à 7) :

| étape | qui appelle | ce qu'il appelle | où cela se défait |
|---|---|---|---|
| `construire_donnees.py` | lui-même | `_charger_ages` | un chargeur : sous `donnees/` au retrait |
| `construire_tableaux_md.py` | lui-même | `carriere_simple`, `simuler` | la question du § 3, ci-dessous |
| `verifier_prose.py` | `mortalite_population.py` | `simuler` | l'étude de la mortalité, dans sa session |
| | `castypes.py` | `pilote.age_de_depart`, `carriere_simple`, `conversion.niveau_relatif` | la même session : le cas type que l'étude bâtit |

L'étude de la mortalité n'est pas de cette étape : la note de la question 3
la range après la session des sondes. Sa sonde, `mortalite_population`, est
la seule des 508 mesures citées qui fasse encore tourner une règle en Python.

**La question laissée au propriétaire : ce que montre le § 3 du README.** Le
§ 3 montre un appel du simulateur Python (`simulateur.simuler`,
`comparaison.tableau()`, `README.md` lignes 653 à 664) puis sa sortie, que la
fabrique écrit ; l'introduction en reprend six lignes pour l'agent de
conduite. Quand le moteur Python part, deux voies.

- *Le bloc montre autre chose.* L'appel Python quitte le README ; à sa place,
  l'adresse du simulateur du site pour la même carrière, et un tableau plus
  court que le script écrit de ce que le pont rend déjà. Coût : la prose du
  § 3 et de l'introduction à reprendre, deux tests à récrire
  (`tests/test_web.py`, vers la ligne 3566 ; `tests/test_simulateur.py`,
  vers 1857) ; `tableau()` part avec le moteur. On perd le détail du
  tableau — le RAFP, le pilier, qui verse la cotisation — ou on le récrit.
- *`tableau()` se récrit sur le résultat que le pont rend.* Ses 170 lignes de
  mise en forme (`simulateur.py`, 337 à 504) passent du côté de la fabrique
  et lisent le dictionnaire du résultat. Tout ce que les deux blocs
  affichent y est, sauf l'écart total, pilier compris, qui se refait de deux
  champs. Les blocs restent à l'octet. Coût : une session courte. Reste
  alors à dire quel appel le bloc de code montre : la façade des tests
  gardera `simuler` et `carriere_simple` servis par le pont, mais dans un
  module fait pour les tests.

Tout ce qui n'en dépend pas est fait ; la seule entrée qui en dépend est
celle de `construire_tableaux_md.py`.

**Ce qui est vérifié, ce qui ne l'est pas.** Vérifié en faisant tourner : les
508 mesures citées, écrites en hexadécimal avant le premier changement et
après chacun des trois lots, sans une différence ; chaque entrée du pont
refaite par son jumeau Python au bit près (`droit_et_refait`) ;
`mesures_accueil.py --verifier` et `construire_tableaux_md.py --verifier` à
jour ; la prose vérifiée ; le relevé par mesure, fichiers mêlés compris :
32 sondes entraient ; hors celle de la mortalité, il n'y reste que les
chargeurs (`Simulateur().macro`,
`.mortalite`) et le type `Carriere`. Trois attentes de mes tests étaient
fausses et ont été corrigées contre la source, non contre le code : l'écart
du scénario 6 n'est pas le rapport de deux pensions quand son départ est
reporté ; la fiche d'une fonctionnaire ne porte pas la contribution de
l'État ; le régime unique vaut 26,35 % sous les conventions de la page Coût,
25,83 % au taux contractuel. Non vérifié : la suite complète, que GitHub
lance ; les sondes sur des données d'ailleurs, qu'aucune ne demande.

**Un défaut de cette étape, réparé le même jour.** Le premier envoi a rougi
la course de GitHub : la suite complète y est passée, mais la garde des
présomptions, qui rejoue la suite rapide sous d'autres valeurs présumées, a
fait échouer un test de `tests/test_sondes_par_le_pont.py`. Il attendait de
l'exemple du README les chiffres que la prose publie, −5,4 % et +25,5 %, sans
dire le jour de naissance : né le 1er du mois, l'écart devient −3,2 %.
L'échec a été reproduit ici (`PRESOMPTIONS_DECALEES=1`), et le test déclare
maintenant la date entière, le 15. La garde entière est verte. La leçon : un
fichier de tests qui naît dans la suite rapide se rejoue sous la garde avant
l'envoi.

**Ce qui ne change pas.** Aucune règle du scénario 1, aucune donnée, aucun
fichier fabriqué, aucune garde. Aucun code du moteur Python n'est retiré.

**Tests.** `tests/test_sondes_par_le_pont.py`, dans la suite rapide
(4 s) ; `python -m pytest -m rapide` ; `tests/test_entrees_du_moteur.py`
(324 s), `test_pont.py`, `test_capitalisation.py`, `test_solde_fusion.py`,
`test_prose.py`, `test_outillage.py`, les confrontations légères, la carte ;
les 172 essais de `tests/js/`.
