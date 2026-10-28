# Étape 14 : le recours à l'ASPA par type de ménage, sur la population

**Le 28 octobre 2026 : le recours que les allocataires servis impliquent,
mesuré sur la population, type de ménage par type de ménage, sur `main`
(28b6249, 24e2d92). Les personnes seules y recourent comme la DREES le mesure
pour les femmes, 49 % en 2016 les sexes recalés sur l'INSEE, pour 50 % ; pas
les hommes, dont le bas manque à la population : 77 à 128 %. Les couples,
65 à 102 % selon la pesée, ne se mesurent pas sans microdonnées ; les trois
cibles d'Ines ne sont pas trois populations d'ayants droit. Comptés comme la
page Coût les compte — la pension de droit direct, chacun à part —, les ayants
droit sont 2,3 à 2,7 millions, trois à cinq fois les servis : sous sa
propre convention, le recours qui redonne les servis est de 20 à 29 %, et non
50, au propriétaire. La population a trop d'hommes aux grands âges. La page
ne bouge pas.**

Demande : la vague du 28 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, le point du bloc de l'étape que le
point 4 de « Ce qui reste » de la note de la vingtième partie
(`2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md`) détaille : le
recours à l'ASPA par type de ménage (Ines), sur la population.

- *Ce qui était.* Le scénario 1 sert l'ASPA à tout ayant droit : il simule une
  carrière, et dit ce que la caisse servirait à qui la demande. La page Coût,
  pour la garantie vieillesse du scénario 6 et pour l'ASPA de l'effet retour,
  retient un recours uniforme de 50 % (`Parametres.taux_recours_garantie`),
  celui que la DREES mesure fin 2016 sur les seules personnes seules (dossier
  n° 97), appliqué à des ayants droit qu'elle compte sur la seule pension de
  droit direct de l'EIR, chacun à part. Ines cale le sien type de ménage par
  type de ménage : parmi les ayants droit de l'enquête Revenus fiscaux et
  sociaux, il tire au hasard autant d'allocataires que ses cibles — 442 756
  personnes seules, 107 923 couples à un allocataire, 12 164 couples à deux en
  2024 (`R/14_minima_pa.R:327-475` au commit `a55816c` ; Ines 2024.1,
  `param_presta_mensuel.xlsx`, onglet Minima, lignes 7 à 9), le total de
  l'ASV et de l'Aspa de son champ réparti selon une structure matrimoniale ;
  ses couples à un allocataire, il les tire parmi ceux dont un seul membre a
  l'âge de l'allocation. Le registre range le point au chantier « 138.14 » :
  le recours que ces effectifs impliquent demande les ayants droit, donc une
  population.
- *Les données*, deux tableaux de l'INSEE, lus le 28 octobre 2026, la DREES ne
  répondant pas à la session :
  - les allocataires du minimum vieillesse au 31 décembre, de 2005 à 2024, par
    tranche d'âge, sexe, isolés ou en couple, que l'INSEE reprend de l'enquête
    de la DREES (`macro/allocataires_minimum_vieillesse.csv`,
    `scripts/fetch/insee_allocataires_minimum_vieillesse.py`) : 753 908 en
    2024, 754 460 pour la DREES ; isolés et en couple somment à l'ensemble à
    dix près depuis 2018, à trois cents de 2009 à 2017 ;
  - la population au 1er janvier par sexe, âge et état matrimonial légal, de
    2006 à 2020 (`macro/etat_matrimonial.csv`,
    `scripts/fetch/insee_etat_matrimonial.py`) : de 60 à 89 ans, ses quatre
    états somment exactement à la population que le modèle lit.
- *La mesure* (`scripts/recours_aspa.py`). Chaque cohorte de la population de
  `grille_large.py`, l'année voulue, à 65 ans ou plus, à sa pension de droit
  direct du scénario 1, sans ASPA — celle que la distribution de 2020
  confronte à l'EIR —, vit en couple dans la part que le recensement de 2021
  donne à son âge et à son sexe ; sinon elle est seule, et veuve dans la part
  que l'état matrimonial légal donne aux veufs de son âge, rapportée à ceux qui
  ne vivent pas en couple (2020 pour 2024). Une veuve touche une réversion,
  55 % de la pension de son mari (54 % au régime général, 60 % à
  l'Agirc-Arrco, 50 % aux fonctionnaires) ; un conjoint est tiré de l'autre
  sexe à l'âge qu'il a, ou aurait, le mari ayant 2,6 ans de plus
  (`Parametres.ecart_age_couple`), sans lien avec la pension de la personne.
  Une personne seule a droit sous le plafond d'une personne seule ; un couple,
  sous le plafond du couple, ses deux pensions comptées, avec un ou deux
  membres en âge de l'allocation ; aucune autre ressource. Les servis : les
  allocataires de 65 ans ou plus ; les couples servis, les allocataires en
  couple moins les couples qui en comptent deux, que l'enquête ne sépare pas —
  entre aucun et autant que de femmes servies, 10,1 % chez Ines. Et les ayants
  droit comme la page les compte : la seule pension de droit direct, chacun à
  part, sous le plafond d'une personne seule pour qui vit seul, sous la moitié
  de celui du couple pour qui vit en couple (`effet_retour.EffetRetour._aspa`).
  La population, simulée une fois sur l'arbre figé de 30717ac (108 minutes sur
  quatre cœurs, 15 406 échecs, ceux de la note de la vingtième partie), se pèse
  en 2016, 2020 et 2024 (un pilote hors du dépôt, qui appelle les fonctions du
  script) ; puis ses têtes, recalées sexe par sexe sur l'INSEE à chaque âge,
  leur total gardé.
- *Les tests* (`tests/test_recours_aspa.py`, sept, rapides) : les deux données
  recoupées à leur source — le total de la DREES, la population du modèle — ;
  la part des veuves parmi les femmes seules de 80 ans en 2020, refaite à la
  main ; et quatre cas posés à la main : une femme seule, veuve ou non, sa
  réversion tirée de deux âges de maris ; deux couples, l'un à un membre en âge
  de l'allocation, l'autre à deux, et ce que l'allocation leur sert ; la
  convention de la page ; les couples servis et le recours. Vus rouges faute
  du script, puis de la fonction de la page.
- *Ce qu'elle trouve*, en milliers de personnes ou de couples de 65 ans ou
  plus, le recours en pour cent ; la population, puis ses sexes recalés :

  | | 2016 | 2020 | 2024 |
  |---|---|---|---|
  | personnes seules servies | 359,3 | 436,1 | 528,7 |
  | personnes seules ayants droit | 581 ; 625 | 743 ; 792 | 658 ; 703 |
  | dont veuves | 133 ; 157 | 131 ; 152 | 103 ; 119 |
  | recours des personnes seules | 61,8 ; 57,5 | 58,7 ; 55,0 | 80,3 ; 75,2 |
  | des femmes seules | 56,7 ; 49,2 | 52,7 ; 46,6 | 70,4 ; 62,3 |
  | des hommes seuls | 78,7 ; 96,0 | 77,1 ; 89,4 | 111,6 ; 127,8 |
  | couples servis, 10,1 % à deux (bornes) | 124 (110 à 137) | 133 (115 à 146) | 148 (122 à 162) |
  | couples ayants droit | 172 ; 144 | 203 ; 176 | 167 ; 145 |
  | dont un seul membre en âge | 15 ; 15 | 17 ; 16 | 12 ; 12 |
  | recours des couples | 72,0 ; 86,0 | 65,3 ; 75,6 | 88,2 ; 101,7 |
  | servis comme la page les compte | 496 | 582 | 691 |
  | ayants droit comme la page les compte | 2 297 ; 2 480 | 2 538 ; 2 731 | 2 351 ; 2 546 |
  | recours sous la convention de la page | 21,6 ; 20,0 | 22,9 ; 21,3 | 29,4 ; 27,1 |

  Dans les couples qui ont droit, l'homme est servi, la femme rarement : 64 et
  21 % en 2016, 73 et 33 % en 2024. Sans réversion, les personnes seules
  ayants droit seraient plus du double, 1 366 000 en 2016 ; à 50 et 60 % de la
  pension du mari, 607 000 et 559 000. Un écart d'âge de cinq ans fait 16 000
  à 23 000 couples à un seul membre en âge, et non 12 000 à 17 000. Servie à
  tous ses ayants droit, l'ASPA de la population vaudrait 2,6 milliards
  d'euros en 2016, dont 2,0 aux personnes seules — la DREES en chiffre 2,1
  pour celles de son champ, 1,3 servis et 0,8 de non-recours —, 3,5 en 2020
  et 3,4 en 2024, quand les comptes de la protection sociale en portent 4,0
  et 4,9. Les réversions que la convention sert aux veufs valent 32 milliards
  en 2020 et 41 en 2024, pour 37 et 42 de droits dérivés (`pensions_droits.csv`).
  La population compte 52 % de femmes de 65 à 69 ans (INSEE 53), 52 de 70 à 79
  (54 à 55), 50 de 80 à 89 (61 à 63), 45 à 90 ans ou plus (74).
- *Ce que cela dit.*
  - Les femmes seules recourent comme la DREES le mesure : 49 % en 2016 les
    sexes recalés, pour 50 % des personnes seules de son champ ; et l'ASPA de
    toutes les personnes seules ayants droit, 2,0 milliards, rejoint ce qu'elle
    chiffre, 2,1. La convention de la réversion porte ce résultat : sans elle,
    les ayants droit doubleraient.
  - Les hommes seuls, non : de 65 à 74 ans, la population compte moins
    d'ayants droit que les caisses n'en servent, en 2024 comme en 2016. Le bas
    des hommes lui manque, celui des carrières très courtes en France ; et
    personne n'y est sans pension, quand l'ASPA en sert certains en entier :
    même servie à tous, son ASPA reste sous ce que les comptes portent.
  - Les couples : 65 à 102 %, et pas moins que les personnes seules. Mais le
    conjoint est tiré sans lien avec la pension de la personne, quand les
    pauvres s'épousent entre eux, et la vie seule sans lien avec la pension
    propre, quand les femmes divorcées ou célibataires ont travaillé plus
    longtemps que les mariées : le recours des couples demande les ménages,
    au CASD.
  - Les trois cibles d'Ines : les caisses servent 80 000 à 160 000 couples à
    un seul allocataire, 110 000 à 135 000 à la part d'Ines ; la population
    n'a que 12 000 à 23 000 couples dont un seul membre a l'âge de
    l'allocation. Les couples à un allocataire sont surtout des couples dont
    les deux membres ont l'âge et dont un seul la demande : il reçoit tout ce
    qui manque au couple, au plus le montant d'une personne seule, et le second
    n'y ajoute que ce qui dépasse (D. 815-1). Le type du couple servi est un
    choix du couple, non une population d'ayants droit.
  - La page compte comme ayants droit 2,3 à 2,7 millions de personnes, trois
    à cinq fois les servis : la veuve, que sa réversion sort de l'ASPA, et
    l'épouse, que la pension de son mari en sort, y ont droit. Son recours de
    50 % y fait deux fois plus d'allocataires que les caisses n'en servent ;
    sous sa convention, celui qui redonne les servis est de 20 à 29 %. La
    garantie est individuelle par construction, et son recours une hypothèse du
    programme ; l'ASPA de l'effet retour, elle, est celle du droit, que le
    ménage borne.
  - La population a trop d'hommes aux grands âges : ses poids sont ceux des
    retraités de 2020 à tous les âges, et l'alignement des survies ne rend pas
    aux femmes leur majorité au-delà de 80 ans. Recalés, les sexes ajoutent
    7 % aux personnes seules ayants droit et ôtent 13 à 16 % aux couples ;
    toute mesure de la population par âge en hérite.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; le scénario 1, qui sert l'ASPA
  à qui y a droit ; la population et ses cas types. Le point d'Ines au
  registre passe `a_trancher` : sa mesure est faite, ce que la page en prend
  revient au propriétaire. Aucune règle du scénario 1 ne change : pas
  d'entrée au journal de veille.
- *Au propriétaire.* La page applique 50 % à des ayants droit qu'elle compte
  sur la seule pension de droit direct, chacun à part. Faut-il, pour l'ASPA de
  l'effet retour, compter comme le droit, la réversion et le ménage compris,
  ou prendre le recours qui redonne les servis sous sa convention, un sur
  quatre ? Et la garantie garde-t-elle 50 %, que la population confirme pour
  les femmes seules ?

**Ce qui reste** de l'étape, en plus de la liste de la note de la vingtième
partie : la part des femmes aux grands âges de la population ; le bas des
hommes seuls, et ceux qui n'ont aucune pension, que l'ASPA sert en entier ; au
CASD, au propriétaire, le recours des couples, l'homogamie et le lien entre la
vie seule et la pension propre.
