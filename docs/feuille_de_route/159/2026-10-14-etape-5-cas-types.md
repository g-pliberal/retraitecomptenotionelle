# Étape 5, les cas types : l'agent de la CNRACL au taux plein, les deux civils entrés tard dans leur régime, le militaire confirmé

**Le 14 octobre 2026 : les trois cas types statutaires sont confrontés aux
départs de 2025 que décrit le jaune pensions annexé au PLF 2027, et les deux
civils recalés sur eux.** L'agent de la CNRACL part au taux plein, et non plus
à l'âge d'ouverture, au niveau de 0,9 salaire moyen, et non plus de 1,1. Sur
la page Coût, les deux civils entrent dans leur régime après six ans sous
contrat pour la génération qui part en 2025, et non plus deux ou aucun : c'est
ce que mesurent les services du jaune. Le militaire ne change pas, le flux de
2025 confirmant le recalage fait sur celui de 2024. Deux défauts que l'ancien
agent de la CNRACL masquait se voient désormais, et sont déclarés.

Demande du propriétaire : « action 159 étape 5 ». La session lui a soumis
trois choix : pour la CNRACL, déplacer le cas type sur l'actif moyen de 2025,
le garder, comme il l'avait décidé le 13 octobre (action 152, étape 2), ou le
scinder ; pour le sédentaire, l'entrée tardive que mesure le jaune sur la page
Coût, la convention du COR gardée, ou l'entrée tardive sur les deux pages ;
pour le militaire, le garder ou lui donner les services du flux de 2025. Sa
réponse, aux trois : « je ne comprends rien, qu'est-ce qui est le plus
propre ? ». La session a donc tranché sur un principe : chaque cas type doit
ressembler au retraité moyen de sa caisse tel que le jaune le décrit, sans
deux erreurs qui se compensent, par les seuls mécanismes que le modèle a déjà.

Le document est celui de l'étape 1 (`sre_jaune_pensions_2027`), tiré de la
branche `jaune-2027` dans `data/brut/`, son empreinte vérifiée ; lu par
`pdftotext -layout`. Les pages citées sont celles qu'il imprime.

## Ce que le jaune dit des trois groupes

- *Les civils de l'État partis pour ancienneté en catégorie sédentaire*
  (tableau B-4, 28 209 départs, 57 % de femmes) : mis en paiement à 64,4 ans,
  à l'indice 735, après 138,1 trimestres de services et 5,2 de bonifications,
  pour 174,5 tous régimes ; taux de 66,8 %, 64,1 % hors décote et surcote, la
  moitié avec une surcote, le cinquième avec une décote ; 2 399 € par mois.
  Leurs services et bonifications tiennent depuis 2004 entre 143 et 148
  trimestres (tableau 95 : 142,9 en 2004, 147,9 en 2017, 144,5 en 2025 ; 146,4
  pour les hommes en 2025), quand l'âge de départ monte de quatre ans :
  rapportés à une carrière commencée à 22 ans et finie à l'âge où le cas type
  part, 60 ans en 2004 et 64 en 2025, ils en laissent deux ans hors du régime
  en 2004, six en 2025. Le tableau 94 date la durée de référence des pensions
  de 2025 : de 165 à 172 trimestres, 167 pour 29 % d'entre elles, 169 pour
  32 %.
- *Les actifs de la CNRACL partis pour ancienneté* (tableau B-5, 10 597
  départs, 70 % de femmes) : mis en paiement à 61,0 ans, à l'indice 508,
  après 127,6 trimestres de services et 6,6 de bonifications, pour 180,7 tous
  régimes ; taux de 60,5 %, 7,8 % seulement avec une décote ; 28,2 % au minimum
  garanti ; 1 578 € par mois. Ils partent de plus en plus tard après leur âge
  d'ouverture, à mesure que la décote monte en charge : 56,2 ans en 2005, 57,2
  en 2011, 58,9 en 2015, 59,6 en 2020, 61,0 en 2025 (tableau 102). Les
  sédentaires de la caisse, deux fois et demie plus nombreux, partent à 64,0
  ans, après 89,9 trimestres de services.
- *Les militaires partis pour ancienneté* (tableaux B-3 et 97, 8 672 départs) :
  radiés à 49,0 ans, à l'indice 605, après 110,9 trimestres de services et
  38,6 de bonifications, pour 154,5 tous régimes ; taux de 66,3 %, plafonné à
  80 % pour le tiers d'entre eux ; 1 943 € par mois. Leur indice de 2025 vaut
  0,86 salaire moyen, au rapport que le cas type donne à son indice de 635 et
  à sa solde de 0,90 : dans la fourchette de 0,83 à 0,98 que l'action 152 avait
  lue de 2003 à 2024 (tableau 98 du jaune 2026). Le tableau 96 en date la
  durée de référence : 11 % encore à 150 trimestres, le régime d'avant 2003.
- *Une incohérence du document.* Au tableau B-5, les services et les
  bonifications de la colonne totale ne sont pas la moyenne de ceux des deux
  versants, pesés de leurs départs : 127,6 trimestres de services aux actifs,
  pour 120,0 ; 89,9 aux sédentaires, pour 87,2 ; 116,3 aux carrières longues,
  pour 110,3. Les effectifs, les âges, les indices, les taux et les pensions
  le sont. C'est la colonne totale qui s'accorde avec son taux de liquidation
  (134,2 trimestres sur 168, à 75 %, font 59,9 %) : la session s'y est tenue.

## Ce qui change

- **L'agent de la CNRACL** (`castypes.py`) part au taux plein et non plus à
  l'âge d'ouverture (règle `taux_plein`), au niveau de 0,9 salaire moyen et non
  plus de 1,1. Le classement lui ouvre ce taux plein plus tôt qu'aux
  sédentaires — la décote s'annule à 62 ans pour les générations nées depuis
  1960 (`categorie_active.csv`) —, et c'est ce que font ses collègues réels.
  Son libellé ne change pas, son commentaire le dit, et la page Cas types aussi
  (`pages.js`, « À quel âge chacun part »).
- **L'entrée tardive** (`macro/hypotheses_projection.yaml`, sous les
  conventions de la page Coût seulement, la page Cas types gardant la carrière
  d'un seul statut). Pour le sédentaire, deux ans sous contrat pour la
  génération 1944, six pour la génération 1961, douze pour la génération 2000,
  quand c'était deux jusqu'à la génération 1962 et huit pour la génération 2000 :
  le niveau et le passé, du jaune (tableau 95) ; la pente d'ici 2000, du COR
  (six ans de services en moins, note 69 de son rapport de juin 2026). Pour
  l'agent de la CNRACL, qui n'en avait pas, six ans pour toutes les
  générations, dans une série à elle (`entree_cnracl`, champ `serie_entree` du
  cas type, `DonneesMacro.delai_entree`). La session lui avait d'abord donné la
  série de l'État : sa pension relative s'écartait alors de 18 % de celle que
  le COR projette pour la CNRACL en 2070, quand elle la suivait à 4 % près sans
  délai — la baisse des services que le COR écrit est celle de l'État.
- **La confrontation au flux de 2025** (`scripts/flux_fonction_publique.py`)
  mesure les cas types tels que la page Coût les pèse
  (`Simulateur.pour_la_projection`), celle où ils portent leur caisse.

L'écart du modèle au jaune, avant et après :

| cas type | âge | durée tous régimes | taux | indice | pension |
|---|---|---|---|---|---|
| sédentaire de l'État, 1961, avant | 64,0 pour 64,4 | 168 pour 174,5 | 75,0 % pour 66,8 % | 749 pour 735 | 2 766 € pour 2 399 € |
| sédentaire de l'État, 1961, après | 64,0 | 168 | 64,3 % | 749 | 2 371 € (−1,2 %) |
| actif de la CNRACL, 1968, avant | 57,75 pour 61,0 | 143 pour 180,7 | 49,7 % pour 60,5 % | 616 pour 508 | 1 506 € pour 1 578 € |
| actif de la CNRACL, 1963, après | 62,0 | 160 | 61,1 % | 511 | 1 535 € (−2,7 %) |
| militaire, 1977 | 48,5 pour 49,2 | 130 pour 154,5 | 59,1 % pour 66,3 % | 635 pour 605 | 1 846 € pour 1 943 € |

Sur la carrière d'un seul statut que la page Cas types montre, les deux civils
resteraient de 14 à 15 % au-dessus du flux : c'est l'entrée tardive qui les
recale, et un test le tient.

## Ce que ça déplace

Aucun des 804 témoins de simulation ; 54 rendus de page sur 70, par les pages
Avantages, Cas types, Coût et Programme surtout.

- *Les avantages de 2024* (`scripts/cout_avantages.py`). Les pensions servies
  avant l'âge légal passent de 12,5 à 8,2 Md€, et celles du classement de 8,3
  à 4,0 : l'agent de la CNRACL en faisait 4,4. Ce que le classement ajoute au
  montant passe de 0,6 à 1,9 Md€ : parti au taux plein, l'agent actif touche
  sans décote ce que l'agent déclassé, parti au même âge, n'a pas, quand les
  deux butaient sur le plafond de vingt trimestres. Le minimum garanti
  retrouve un montant, 7 M€ en 2024 et 174 en 2000 : l'agent de la CNRACL des
  générations anciennes, à 0,9 salaire moyen après six ans de contrat, s'en
  approche — 28,2 % des actifs de 2025 y sont. Sa fiche
  (`avantages_non_contributifs.yaml`) perd la raison qu'elle donnait de n'en
  pas avoir. En tout, 99,3 Md€ au lieu de 97,9, dont 17,2 calculés au lieu de
  15,8, pour 22 dispositifs chiffrés au lieu de 21.
- *La page Coût.* L'écart du passé au scénario 4 passe de −51,8 à −51,6 % ;
  la trajectoire propre de 2070, de 14,8 à 14,9 % du PIB. Face au COR, à
  l'horizon (`test_l_ecart_au_cor_groupe_par_groupe`) : la pension relative
  de la FPE de +9,3 à +5,2 %, sa dépense de +24,8 à +19,9 % ; la pension
  relative de la CNRACL de +3,2 à +0,2 %, et sa dépense de +1,5 à +10,9 % —
  le seul cliquet qui remonte, dit plus bas.
- *La proposition.* Son solde moyen de 2026 à 2070 passe de −0,85 à −0,92
  point de PIB, sa dette de 2070 de 56 à 62 % du PIB, le creux de son
  coefficient de 0,85 à 0,84 ; la variante prospective de −3,0 à −3,1 point.
  L'agent de la CNRACL parti tôt était celui que le notionnel pénalisait le
  plus : parti au taux plein, il fait moins d'économie. L'accueil cite ces
  chiffres (`MESURES_BLOCAGES`), et la baisse médiane qu'il donne à un
  retraité d'aujourd'hui passe de 29 à 28 % ; le parcours de présentation
  suit.
- *Les tests.* Ceux qui tenaient l'ancien agent actif sont récrits sur le
  nouveau : la confrontation au flux (`test_flux_fonction_publique.py`, le
  test des deux erreurs qui se compensaient devenant celui de l'entrée
  tardive qui recale les civils) ; les retraités de moins de soixante ans
  (`test_avantages.py`), qui cède comme son docstring l'annonçait ; les âges
  d'équilibre de deux cas types d'un même vingtile (`test_cycle_de_vie.py`),
  l'agent actif passant du quatorzième vingtile au onzième — le salarié au
  SMIC et l'exploitant agricole le montrent désormais ; le délai d'entrée
  (`test_cout.py`).

## La population remesurée

`grille_large.py --grille population`, comme l'action 152 le fait à chaque cas
type déplacé. La place de la CNRACL, en pour cent de ses retraités de chaque
sexe, l'avant étant celui que la note de l'étape 2 de l'action 152 relevait le
13 octobre :

| CNRACL | q1 | q2 | q3 | q4 | q5 |
|---|---|---|---|---|---|
| hommes, EIR | 0,0 | 1,8 | 39,8 | 42,2 | 16,1 |
| hommes, avant | 3,3 | 10,3 | 50,7 | 22,2 | 13,4 |
| hommes, après | 0,0 | 6,7 | 59,7 | 18,3 | 15,3 |
| femmes, EIR | 0,0 | 4,3 | 43,0 | 38,4 | 14,3 |
| femmes, avant | 5,1 | 27,9 | 43,0 | 15,8 | 8,2 |
| femmes, après | 0,0 | 43,5 | 38,1 | 11,7 | 6,6 |

Le premier quintile se vide, le taux plein ôtant la décote ; le niveau ramené
de 1,1 à 0,9 salaire moyen fait descendre le reste, et les femmes surtout : la
population décline le cas type sur la dispersion des salaires du privé de
chaque sexe, trop large pour une grille indiciaire, et le traitement trop haut
de l'ancien cas type la compensait en partie — le chantier à part que le
propriétaire a décidé le 13 octobre (action 152, étape 2). Les civils de l'État
s'y rangent à 0,0, 3,3, 20,4, 36,9 et 39,3 % chez les hommes, pour 0,1, 0,5,
13,9, 27,6 et 58,0 dans l'EIR : un peu bas, comme l'action 152 le disait. Le
reste bouge à peine : 14,4 % des hommes au minimum, pour 14,3 le 12 octobre et
9,8 dans l'EIR ; des bornes de quintiles à 989, 1 314, 1 651 et 2 190 €.

## Deux défauts que l'ancien cas type masquait

- **Le pilote ignore la montée en charge de la décote de la fonction
  publique.** La liquidation l'applique (`DecoteFonctionPublique`) : pas de
  décote avant 2006, puis un âge d'annulation égal à la limite d'âge moins un
  nombre de trimestres qui décroît de seize en 2006 à zéro en 2020
  (`decote_fonction_publique.csv`). Le pilote, qui date le taux plein
  (`ouvrir.age_taux_plein_droit`), lit la limite d'âge entière et la durée du
  taux maximum : il fait attendre à l'agent de la CNRACL 59 ans et demi ou 60
  pour les générations 1940 à 1956, quand les actifs partaient à 56,2 ans en
  2005, 57,2 en 2011, 58,9 en 2015. Lu avec le barème, le taux plein
  tomberait à l'ouverture, 55 ans, jusqu'à la génération 1950, puis
  monterait de 56 ans pour la génération 1951 à 61 ans et quart pour celle de
  1960 : presque l'âge du tableau 102, année par année. La grille part désormais
  jusqu'à deux tiers d'année plus tard que l'âge conjoncturel de la DREES, de
  2008 à 2011, et de 0,29 an en moyenne, pour 0,07 : la fenêtre est déclarée
  (`test_age_conjoncturel.py`, `ANNEES_DE_LA_DECOTE`), comme le constat que le
  contrefactuel par catégorie socioprofessionnelle est désormais plus près
  de l'âge réel que les fiches (`test_cout_age_depart.py`). L'ancien agent,
  parti à 55 ans, compensait ce défaut et l'absence, dans la grille, des
  départs anticipés pour carrière longue du privé des années 2004 à 2011.
  Corriger le pilote touche au scénario 1, en Python et en JavaScript : une
  tâche à part.
- **Un seul cas type actif porte la CNRACL.** Ses têtes croissent comme la
  population qui a passé son âge de départ : à 62 ans, de 7 % de plus d'ici
  2070 que les retraités que le COR projette à la caisse, quand elles
  croissaient de 4 % de moins à 57 ans, et sa pension relative de 3 % de
  plus. Le COR fait monter l'âge moyen de départ à la CNRACL de 61,5 à 64,3
  ans avec ses sédentaires (Canopée, au registre, chantier 138.3) ; le cas
  type, actif, reste à 62. Le cliquet de la dépense de la CNRACL remonte de 2
  à 11 %, avec cette raison ; Canopée, au registre des modèles, la porte.

## Le militaire, confirmé

Le flux de 2025 confirme le recalage fait le 12 octobre sur celui de 2024
(action 152, étape 1) : radié à 48,5 ans pour 49,0, à un indice 5 % trop haut,
sa pension 5 % trop basse. Ce qui lui manque est ce que le simulateur ne saisit
pas : les bénéfices de campagne et la bonification du service aérien, 18,6
trimestres en plus du cinquième, 38,6 en tout pour 20 au cas type. Lui donner
les services de 2025, 27,75 ans au lieu de 27,5, aurait déplacé toutes les
pages pour moins d'un point de pension : il ne change pas.

## Ce qui reste

- **Le pilote et la décote de la fonction publique**, au scénario 1 : une
  tâche proposée au propriétaire, qui resserrera la fenêtre de
  `test_age_conjoncturel.py`.
- **La CNRACL en deux cas types**, actif et sédentaire, à la part que le jaune
  donne à chacun : il faut d'abord un partage de la caisse entre cas types
  autrement qu'à parts égales (`castypes.poids_effectifs`) — le chantier 138.3.
- **Les bonifications du militaire** que le simulateur ne saisit pas, et son
  second métier ; **la polypension sur la page Cas types**, où les civils
  gardent une carrière d'un seul statut.
- **Le tableau B-5**, dont les services de la colonne totale ne recoupent pas
  les versants : à signaler, si le propriétaire le veut, à la direction du
  budget.
