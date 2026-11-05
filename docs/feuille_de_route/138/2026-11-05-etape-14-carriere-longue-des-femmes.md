# Étape 14 : la carrière longue des femmes de 1953 — la règle est juste ; ce qui leur manque est le chômage que la population donne à toute carrière de trente à quarante ans

**Reprise, au 5 novembre 2026.** Fait : chaque grille contre l'EIR en 2020 ; la population, du 16 au 28 octobre (décote, natures, hommes selon le
rang, ASPA, invalides, décote entre les deux âges et des résidents, surcote des statutaires, limites) ; le pilote des carrières inactives ; au
modèle, la descente, le militaire au mois ; le 3 novembre, le taux plein des femmes entre les deux âges, les agents décotés, la surcote du
salariat, sa mesure au dépôt, les écarts de R-I-bis, la décote d'après 1960, relue par R-I-ter, retouchée le 5. Le 5 aussi : la durée des femmes,
le calage tient ; la carrière longue des femmes de 1953, la cause est dans la population ; les inaptes, trente-huitième version ; le taux plein
par l'âge, mesuré, rien ne change (l'EIR à un demi-point près, sauf les hommes de 1953, 4,5 % pour 5,8). Reste, une session par point : les
artisans (une source), les saisonniers agricoles ; les femmes âgées ; les départs après 67 ans, avec ceux d'après l'âge du taux plein. Au
propriétaire : 152, 157, le CASD, l'incitation, le militaire, la sonde au mois, le recours de la page, les hommes entre les deux âges, la surcote
d'après 1953, la décote d'après 1960, la carrière complète, le juge de 1955, les natures des carrières de trente à quarante ans, la carrière longue
des fonctionnaires de 1953. Détail : `…-carriere-longue-des-femmes.md`, `…-inaptes.md`, `…-taux-plein-par-l-age.md`.

**Le 5 novembre 2026 : les femmes nées en 1953 de la population partent en
carrière longue pour 6,6 % de leurs départs, quand l'EIR de 2020 en compte
13,2 % des résidentes. La mesure, refaite au même script, redonne chaque
ligne de celle du matin. La règle n'y est pour rien : le modèle applique à la
génération 1953 les portes de D. 351-1-1 et les périodes réputées cotisées de
D. 351-1-2 dans leurs rédactions du 1er novembre 2012, lues au texte, et la
durée de 165 trimestres du décret du 30 décembre 2010. Le manque est dans la
population : 64,9 % de ses femmes n'ont pas cinq trimestres validés à la fin
de l'année de leurs 20 ans, dont toutes les statutaires (20,3 points) ; et
26,3 % les ont, mais pas la durée cotisée, parce que toute carrière de trente
à quarante ans du salariat privé porte, au milieu, en chômage indemnisé, la
part assimilée moyenne de sa classe, huit années à la médiane, quand la
carrière longue n'en répute cotisés que deux trimestres. L'échantillon
interrégimes ne trouve du chômage qu'à 38,3 % des femmes nées en 1950. Aucune
source publiée ne dit qui, parmi ces carrières, n'a aucune période assimilée :
la convention va au propriétaire. Aucun code ne change, rien ne bouge.**

Demande : la vague 7, lancée le 5 novembre 2026 par la session
d'orchestration, file I : l'action 138, étape 14, le point 3 de « Ce qui
reste » de `2026-11-05-etape-14-calage-de-la-duree-des-femmes.md`, « la
carrière longue des femmes de 1953 de la population, 6,6 % pour 13,2 ».
Mesurer d'abord, puis trouver la cause : distinguer ce qui vient de la règle
(D. 351-1-1 en vigueur pour la génération 1953) de ce qui vient de la
population (l'âge de début, la durée cotisée, les trimestres d'enfants ou de
chômage) ; corriger la règle si le texte est net, la population seulement si
une source publiée la fonde.

- *La mesure refaite* (`docs/mesures/138/2026-11-05-etape-14-carriere-longue-des-femmes.txt`,
  ses trois scripts et leurs sorties), sur `main` à 8a5adc6. Le script de la
  mesure du matin (`2026-11-05-etape-14-duree-des-femmes.txt`), inchangé,
  `python pilote.py 1953 2020 1955 2022`, redonne chacune de ses lignes, pour
  1953 comme pour 1955, à l'identique : carrière longue 6,6 %, âge légal 61,3,
  avant lui 11,5, entre les deux âges 14,9. La source publiée est la même :
  « Caractéristiques des retraités nés en 1953 (EIR 2020) », feuille
  « Naissance-Résidence », ligne 272, « Part de départs anticipés pour
  carrière longue (en %) », femmes résidentes, 13,2, lue au classeur par la
  note du matin, qui en donne l'adresse et l'empreinte.
- *La règle, relue au texte* pendant la session, dans l'index LEGI de la DILA
  (`python scripts/fetch/dila_cherche.py legi --num D351-1-1 --titre "securite sociale"`).
  - D. 351-1-1, rédaction en vigueur du 1er novembre 2012 au 1er septembre
    2023 (LEGIARTI000026139949) : « I.-L'âge prévu au premier alinéa de
    l'article L. 351-1 est abaissé […] à soixante ans, pour les assurés qui
    justifient d'une durée d'assurance cotisée […] au moins égale à celle
    prévue au deuxième alinéa de l'article L. 351-1 et qui ont débuté leur
    activité avant l'âge de vingt ans » ; « B.-Pour les assurés nés en 1953 :
    1° A cinquante-six ans […] majorée de huit trimestres et ayant débuté leur
    activité avant l'âge de seize ans ; 2° A cinquante-huit ans et quatre mois
    […] majorée de quatre trimestres et ayant débuté leur activité avant l'âge
    de seize ans ; 3° A cinquante-neuf ans et huit mois […] au moins égale à
    celle prévue au deuxième alinéa de l'article L. 351-1 et ayant débuté leur
    activité avant l'âge de dix-sept ans ». Les lignes `2012.833` de
    `carriere_longue.csv` qui couvrent 1953 disent les mêmes quatre portes :
    20 ans, 60,00, plus zéro ; 16 ans, 56,00, plus huit ; 16 ans, 58,33, plus
    quatre ; 17 ans, 59,67, plus zéro (58 ans et 4 mois = 58 + 4/12 = 58,33 ;
    59 ans et 8 mois = 59 + 8/12 = 59,67). La rédaction d'avant
    (LEGIARTI000023397567, du 1er juillet 2011 au 1er novembre 2012), « IV. ―
    Pour les assurés nés en 1953 : 1° A cinquante-six ans […] avant l'âge de
    seize ans ; 2° A cinquante-huit ans et quatre mois […] », a les deux
    premières portes des lignes `2011.5` de 1953, 56,00 et 58,33 avant
    16 ans.
  - La durée : « sont fixées à 165 trimestres pour les assurés nés en 1953 et
    1954 » (décret n° 2010-1734 du 30 décembre 2010, article 9,
    JORFARTI000023334359) ; les départs que la sortie nomme lisent 165
    (`trimestres_requis`).
  - D. 351-1-2, rédaction du 1er novembre 2012 au 1er avril 2014
    (LEGIARTI000026139944) : sont réputés cotisés le service national, « dans
    la limite de quatre trimestres » ; l'incapacité temporaire, « dans la
    limite totale de six trimestres, sans que le nombre total de périodes
    validées en application des 1° et 5° de l'article R. 351-12 ne puisse
    excéder quatre trimestres » ; le chômage, « dans la limite de deux
    trimestres ». C'est la version `deux_trimestres_de_chomage` de la fiche
    `carriere_longue_reputes_cotises_autres` : service 4, incapacité 4,
    incapacité et maternité 6, chômage 2. L'AVPF n'y est pas : la fiche ne la
    répute cotisée que depuis septembre 2023.
  - Les trimestres d'enfants : D. 351-1-2-1, qui en compte « dans la limite
    de deux trimestres », n'existe que depuis le décret n° 2026-700 du
    29 juillet 2026 et « s'appliquent aux pensions prenant en effet à compter
    du 1 er septembre 2026 » (LEGIARTI000054589209) ; aucune femme de 1953
    n'en a, et le modèle ne lui en donne pas
    (`ENFANTS_REPUTES_COTISES_DEPUIS`).
  - La règle est donc celle du texte ; aucune erreur ne s'y trouve.
- *La décomposition* (`pilote_cl4.py`). Pour chaque femme née en 1953 qui ne
  part pas en carrière longue, sa carrière rebâtie au moteur Python à
  60 ans, et à 61 ans et 1 mois, le mois qui précède l'âge légal (61 ans et
  2 mois) : l'entrée précoce lue comme le modèle la lit
  (`CarriereLongue._entree_precoce`, cinq trimestres validés à la fin de
  l'année des 16, 17 et 20 ans), et la durée cotisée, réputée comprise
  (`ligne_cotisee`, `CarriereLongue._reputes_assimiles`), contre les 165
  trimestres. En pour cent des départs des femmes de 1953, pesés comme la
  mesure du matin :

  | | part | calcul |
  |---|---|---|
  | parties en carrière longue | 6,57 | 2,03 (trente à quarante ans) + 4,54 (carrières pleines) |
  | l'ont, ne la prennent pas | 2,32 | 0,78 (à 60 ans) + 0,56 + 0,98 (avant l'âge légal) |
  | entrées avant 20 ans, durée cotisée courte | 26,26 | 18,70 (trente à quarante ans) + 7,56 (carrières pleines) |
  | sans cinq trimestres à la fin de l'année des 20 ans | 64,85 | 37,89 (à l'âge légal) + 9,94 (entre) + 12,10 (à l'annulation) + 4,92 (avant) |
  | total | 100,00 | 6,57 + 2,32 + 26,26 + 64,85 |

  - *Celles qui l'ont et ne la prennent pas*, 2,32 : toutes des carrières du
    salariat privé, 1,53 parties plus tard avec une surcote (0,52 + 1,01),
    0,79 à l'âge légal (0,27 + 0,52), toutes ces dernières des variantes
    `surcote1.21`, parties à 61,213 ans, la sortie les nomme une à une. Ce
    sont des départs choisis (`DEPARTS_AVEC_SURCOTE`), non un défaut de la
    règle.
  - *Celles qui entrent avant 20 ans et manquent la durée*, 26,26 : il leur
    manque, au mois qui précède l'âge légal, de 1 à 4 trimestres pour 3,44
    d'entre elles, de 5 à 8 pour 5,93, de 9 à 20 pour 2,57, 21 et plus pour
    14,33 (somme 26,27, à l'arrondi). Pour 25,90 (18,62 + 7,28), leurs
    périodes assimilées non réputées cotisées suffiraient à le combler ;
    pour 20,66 (18,62 + 2,04), leur seul chômage. Elles en ont en moyenne
    25,81 trimestres validés sans cotisation : 20,12 de chômage indemnisé,
    4,74 d'AVPF, 0,95 de maladie ; 2,10 en sont réputés cotisés. Elles
    partent pour 22,64 à l'âge légal, 3,48 entre les deux âges, 0,15 à
    l'annulation (somme 26,27).
  - *Celles qui n'ont pas l'entrée*, 64,85 : les statutaires, 20,26 (CNRACL
    8,41, État civil 10,16, militaire 0,40, régimes spéciaux 1,29) ; les
    carrières courtes du salariat privé, 30,05 (moins de dix ans 7,21, de dix
    à vingt 10,39, de vingt à trente 12,45), à qui la durée manquerait de
    toute façon ; ses carrières longues entrées après 20 ans, 9,37 (trente à
    quarante ans 5,95, pleines 3,42) ; les non-salariés agricoles, 4,44 (0,43
    + 0,62 + 0,74 + 1,62 + 1,03) ; les libéraux, 0,66 (0,10 + 0,12 + 0,27 +
    0,17). Somme 64,78 ; le reste, 0,07, en lignes de moins de 0,1 que le
    script n'imprime pas.
- *La cause : le chômage de chaque carrière de trente à quarante ans.* Sous
  `ASSIMILEES_SELON_LE_RANG`, chaque classe de centiles d'une tranche de
  durée prend la part assimilée des quintiles de l'EIR que ses rangs
  couvrent, et `decalages_de_tranche` en fait, pour TOUTE carrière de la
  classe, un bloc de chômage indemnisé au milieu de la carrière. Les
  carrières pleines, elles, ont leurs natures à leur part depuis le
  23 octobre (`NATURES_A_LEUR_PART`) : une classe sans nature n'y a aucune
  année assimilée. Pas celles de trente à quarante ans. `exemple.py` le
  montre : parmi les femmes du salariat privé des deux tranches longues, les
  61,2 % de trente à quarante ans ont toutes des années assimilées, aucune
  ligne « 0 » ; les carrières pleines sans aucune, 1,9 + 7,8 = 9,7 % de ces
  femmes. La carrière de trente à quarante ans de la classe p50, la plus
  lourde, entre en 1972, à 19 ans, et valide jusqu'en 2013, ses 60 ans :
  2013 − 1972 + 1 = 42 années, 168 trimestres ; elle est au chômage de 1989
  à 1996, 8 années, 32 trimestres ; elle en cotise 168 − 32 = 136, en
  répute deux de chômage, 136 + 2 = 138, et il lui en manque
  165 − 138 = 27. Elle a l'entrée et la durée validée d'une carrière
  longue, pas sa durée cotisée.
- *Ce que les sources disent.*
  - L'EIR de 2020, génération 1953, femmes de tous lieux de résidence, par
    quintile de la pension en équivalent carrière complète
    (`quintiles_eqcc_generations.csv`, certifié, feuille « QuintilesEQCC ») :
    durée cotisée et durée validée hors majorations, en années, et part des
    départs en carrière longue. Premier quintile, 17 et 26, 1,7 % ; deuxième,
    29 et 37, 10,8 % ; troisième, 37 et 40, 22,4 % ; quatrième, 38 et 40,
    24,4 % ; cinquième, 39 et 40, 13,2 % ; ensemble, 30 et 35, 12,9 %. Les
    femmes du deuxième quintile ont en moyenne (37 − 29) / 37 = 21,6 % de leur
    durée sans cotisation, huit années, et pourtant 10,8 % d'entre elles
    partent en carrière longue, qui demande 165 trimestres cotisés ou réputés
    tels : leurs années assimilées ne sont pas les mêmes pour toutes. La
    moyenne de la classe, donnée à chacune, ferme la porte à toutes.
  - L'échantillon interrégimes de cotisants de 2017 (`natures_assimilees.csv`,
    certifié, indicateur « Part_aff », champ « Aff_avant_23ans ») : des
    femmes nées en 1950 affiliées avant 23 ans, 38,3 % ont validé un
    trimestre de chômage à 67 ans, 39,8 % un d'AVPF, 20,2 % un de maladie ;
    des nées en 1954, à 63 ans, 44,2, 43,9 et 24,1. La population en donne à
    toutes les carrières de trente à quarante ans.
  - Ce qu'aucune ne dit : la distribution jointe des natures — combien de
    femmes n'ont aucune période assimilée —, ni comment elle se répartit
    entre les tranches de durée et les rangs. Les parts de l'échantillon
    bornent seulement la part des femmes qui n'ont aucune des trois natures :
    au moins 100 − 39,8 − 38,3 − 20,2 = 1,7 % des nées en 1950 si les natures
    ne se recouvrent jamais, au plus 100 − 39,8 = 60,2 % si elles se
    recouvrent toutes. La convention qui donne aux carrières pleines leurs
    natures selon le rang (« le service et l'AVPF du bas des rangs, le chômage
    et la maladie du haut ») est une convention, choisie le 23 octobre ;
    l'étendre aux carrières de trente à quarante ans en serait une autre.
- *La convention qu'il faudrait choisir* (au propriétaire) : donner aux
  carrières de trente à quarante ans, comme aux pleines, leurs natures à leur
  part (`NATURES_A_LEUR_PART`, `classes_de_nature`) — une part d'entre elles
  sans aucune année assimilée, les autres avec l'AVPF, le chômage ou la
  maladie, aux parts de l'échantillon, sous la masse que l'EIR donne à leur
  classe —, ou garder le bloc d'aujourd'hui. Ce qu'elle déplacerait, borné
  par la mesure : la carrière longue des femmes de 1953 resterait entre 6,57
  (rien ne change) et 6,57 + 18,62 = 25,19 (aucune de ces carrières n'a de
  chômage), 6,57 + 25,90 = 32,47 si aucune des deux tranches n'avait de
  période assimilée non réputée ; l'EIR, 13,2, est entre. À titre
  d'illustration, non de mesure : si le chômage n'allait qu'à la part des
  femmes qui en ont dans l'échantillon, et qu'aucune autre nature ne le
  remplaçait, 18,62 × (1 − 0,383) = 11,49 et 18,62 × (1 − 0,442) = 10,39
  points de plus, 18,06 ou 16,96 en tout : au-dessus de l'EIR, ce qui dit
  que la part de l'AVPF et de la maladie, et leur rang, décideraient du
  résultat. Les 22,64 points de ces femmes à l'âge légal sont aussi presque
  tout l'excès de l'âge légal, 61,3 − 37,5 = 23,8 : la même convention
  déciderait des deux.
- *La carrière longue des fonctionnaires* (au propriétaire) : les statutaires
  de la population, 20,26 % des femmes de 1953, entrent toutes après 20 ans
  et n'en ont aucune. Le jaune des pensions de 2027
  (`caracteristiques_fonction_publique.csv`, tableau B-2, flux de 2025) en
  compte 5 940 départs de femmes à la CNRACL et 2 409 chez les civils de
  l'État : sous le droit de 2023, non celui de la génération 1953. Aucune
  source du dépôt ne dit la part des fonctionnaires nées en 1953 parties en
  carrière longue ; sans elle, leur âge d'entrée reste ce qu'il est.
- *Ce qui ne bouge pas.* Aucun code, aucune donnée, aucun test : la
  convention attend le propriétaire. La grille du coût (décision 11) n'est
  pas touchée : la convention ne porterait que sur la population. La page,
  qui ne lit pas la population (action 157), les témoins, le paquet. Aucune
  règle du scénario 1 : pas d'entrée au journal de veille. Les artisans
  (décision 12) n'entrent pas ici.
- *Relevé en chemin, hors de la tâche* : les variantes `surcote1.21` des
  carrières du salariat privé qui ont la carrière longue à 60 ans partent à
  61,213 ans, un demi-mois après l'âge légal de 1953 (61 ans et 2 mois),
  rangées au taux plein à l'âge légal (0,79 point des femmes) ; un départ
  « avec surcote » qui n'en a pas le temps. Non corrigé.

**Ce qui reste**, de ce point :

1. *Au propriétaire* : la convention des natures des carrières de trente à
   quarante ans (ci-dessus), et, s'il la choisit, la règle de rang qui
   répartit entre elles l'AVPF, le chômage et la maladie ; puis la mesure de
   la génération 1953, au même script.
2. *Au propriétaire* : une source qui dise la part des fonctionnaires nées
   en 1953 parties en carrière longue, ou leur âge de début d'activité.

Renvoi du 5 novembre 2026 : la ligne 272 de « Naissance-Résidence » est la ligne 273 (la ligne « Femme »), dans `2026-11-05-retouches-6.md`.
