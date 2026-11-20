# Avant l'étape 3 de la note 0009 : la carrière longue aux bascules de 2023 et de 2026

**Reprise, au 20 novembre 2026.** L'étape 3 de la note de décision 0009 n'est
pas lancée : le propriétaire a demandé d'abord cette vérification, et décide
de la suite. Elle est faite. Quand un régime attend son ouverture après le
départ déclaré, le moteur lisait la carrière longue et la durée requise dans
le texte du départ déclaré ; il les lit maintenant dans le texte de chaque
date d'effet essayée, les durées restant celles du départ déclaré, et sans
reculer une date que le texte du départ ouvrait. Reste, au propriétaire :
lancer ou non l'étape 3, dont le brief est « Pour l'étape 3 » dans
`/mnt/project-files/architecture/191-briefs-amendes.md` ; et écrire ou non
la clause de sauvegarde de l'article 8 du décret n° 2023-436, dont le moteur
ne garde que la date. Le détail est dans cette note.

Le 20 novembre 2026, une session de vérification, sur le choix du
propriétaire au point d'arrêt de l'étape 2 (« Vérifier d'abord la carrière
longue »).

**Ce que le moteur rendait.** La date à laquelle un régime sert sa pension
après le départ déclaré (`ouvertureDe`, `moteur/js/droit/departs.js`) ne sert
qu'aux carrières à plusieurs régimes dont l'un liquide au départ et l'autre
attend : l'aide-soignante partie de l'hôpital avant l'âge légal, dont le
régime général attend. Une carrière d'un seul régime, déclarée avant
l'ouverture, garde son départ déclaré, dit « non ouvert ». Pour l'âge légal,
la recherche essayait déjà chaque version ; pour la carrière longue et la
durée requise, elle lisait le texte du départ déclaré
(`CarriereLongue.portes`, `dureeRequise`), puis liquidait à la date trouvée
sous le texte de cette date.

**Deux écarts mesurés, dans le moteur.**

- Bascule du 1er septembre 2023 (décret n° 2023-436, article 9 : « pensions
  prenant effet à compter du 1er septembre 2023 »). Née le 15 mars 1965,
  entrée à quatorze ans, 174 trimestres cotisés, partie de l'hôpital le
  1er août 2023 : la rédaction de 2012 lui demande 169 + 8 trimestres pour
  partir à 58 ans, celle de 2023 les 172 de sa génération. Le moteur servait
  son régime général le 1er avril 2025, à ses 60 ans de la rédaction de 2012 ;
  le texte l'ouvre le 1er septembre 2023.
- Bascule du 1er septembre 2026 (loi du 30 décembre 2025, article 105 ;
  décret n° 2026-345). Née le 15 juin 1965, 171 trimestres cotisés, partie le
  1er août 2026 : L. 161-17-3 lui en demandait 172, il lui en demande 171 à
  compter de septembre. Le moteur servait son régime général le
  1er juillet 2028, à l'âge légal ; le texte l'ouvre le 1er septembre 2026.
  Régime général et Agirc-Arrco, 5 385 euros par an, servis vingt-deux mois
  plus tôt.

La mesure hors moteur de l'évaluation du 18 novembre (`fenetres_cl.py`)
supposait la durée acquise. Dans le moteur, l'écart de 2026 ne tient presque
jamais à la porte seule : qui n'a que la porte des vingt ans n'a pas ses 172
trimestres cotisés avant 60 ans et 9 mois. Il tient à la durée requise, qui
baisse d'un trimestre pour les nés de 1964 et de 1965. À la bascule de 2023,
il va dans les deux sens : plus tôt par la porte des seize ans, qui perd ses
huit trimestres de plus, et par celle des dix-huit ans, qui naît ; plus tard
pour les nés à compter de septembre 1963.

**La correction.** `ouvertureDe` parcourait déjà les mois qui suivent le
départ déclaré, et recalculait l'ouverture quand les périodes des régimes
changent. Elle recalcule aussi quand changent les portes de la carrière
longue ou la durée requise de la date d'effet (`droitDeLaDate`), sur la
carrière vue à cette date (`liquideeAu`). Les durées sont celles du départ
déclaré : la carrière n'a pas de ligne après lui. Test tiré des deux textes,
vu rouge :
`test_la_carriere_longue_s_ouvre_a_la_premiere_date_dont_le_texte_l_ouvre`
(`tests/test_departs.py`). Aucun des 937 cas de `simulations.json` ne bouge ;
les tests rapides sont verts.

**La clause de sauvegarde de 2023, pour la date seulement.** L'article 8 du
décret n° 2023-436 garde aux nés du 1er septembre 1961 au 31 décembre 1963
qui avaient, avant le 1er septembre 2023, la durée de l'ancienne rédaction,
l'âge de cette rédaction pour une pension qui prend effet après. La
circulaire Cnav 2023-14, point 9.2, lue le 20 novembre, en donne un exemple :
née le 13 octobre 1963, 168 trimestres cotisés au 30 juin 2023, la retraite
anticipée prend effet le 1er novembre 2023, à 60 ans, au taux plein
(L. 351-8, 4° ter), proratisée sur la durée nouvelle (170/170). La recherche
seule aurait reculé cette date à l'âge légal : elle garde donc la date de la
carrière longue acquise sous le texte du départ déclaré quand un texte
postérieur la reculerait (`gardeeParLeTexteDuDepart`), et l'exemple de la
circulaire est un test
(`test_la_clause_de_sauvegarde_de_2023_garde_l_age_de_la_redaction_d_avant`).
Aucune date ne recule donc par rapport à la veille ; celles que le texte
avance avancent.

**Ce qui reste faux, comme la veille.** Les bornes de la clause ne sont pas
écrites : une date de plus dans le code ferait monter le cliquet des
constantes datées, et sa place est dans les versions de la fiche
`carriere_longue`. Un assuré né après 1963, parti avant septembre 2023 avec
la durée de l'ancienne rédaction, garde donc lui aussi la date de l'ancienne
rédaction, que le texte ne lui garde pas. Et la liquidation ne lit pas la
clause : à la date gardée, elle dit le droit « non ouvert » et ne donne pas
le taux plein du 4° ter de L. 351-8 ; de même pour qui déclare son départ
après le 1er septembre 2023 avec 168 trimestres. L'écrire demande une fiche
de catégorie au taux plein (`moteur/js/droit/categories.js`), la durée
acquise avant le 1er septembre 2023 sans l'AVPF, et de savoir ce qu'en font
la fonction publique et les complémentaires : une session à elle.

**Ce qui reste à l'étape 3.** La recherche lit encore les portes par
`CarriereLongue.portes` et la durée par `dureeRequise` : les migrer vers les
versions de leurs fiches ne devrait plus déplacer de résultat. L'âge proposé
d'un cas type (`ageCarriereLongue`, `moteur/js/droit/ouvrir.js`) lit toujours
le texte du départ déclaré, ce qui est juste : il répond à ce départ-là.
