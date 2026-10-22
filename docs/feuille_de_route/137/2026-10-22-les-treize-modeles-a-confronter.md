# Les treize modèles « jamais confrontés » : ce qui l'a vraiment été

**La demande**, le 22 octobre 2026 : la vague du jour, où la session de suivi
« Qu'est-ce qu'il reste à faire ? » lance, sur la demande du propriétaire
(« Lance une session par action qui n'a pas besoin de moi »), une session par
action qu'une session peut avancer sans lui. Pour l'action 137 : le tableau de
bord (`docs/etat.md`, « Les autres modèles ») comptait treize modèles du
registre à confronter au scénario 1 en premier, au code ouvert et jamais
confrontés, quand le bloc « Reprise » ne les nommait plus et que la feuille de
route disait EDIFIS confronté sur les taux de cotisation : « Établis, modèle
par modèle, ce qui a vraiment été confronté, et fais que le registre
(`data/reference/referents.yaml`) et le tableau de bord disent vrai. »

**Fait, le 22 octobre 2026 : la remise à plat ; neuf l'avaient été, ou le
sont ce jour, quatre jamais.**

- *Ce que le tableau de bord comptait.* Est confronté, pour lui, un modèle
  dont la ligne nomme la version confrontée (`version`) ou des valeurs
  entrées au manifeste. Aucun des treize n'avait de `version` : tous avaient
  été lus, le 1er octobre pour le registre et le 4 pour le relevé de l'action
  138, et leur note disait « comparé au dépôt » au commit lu, la place que
  l'en-tête du registre donne à la version « seulement lue ». Le critère
  retenu ici : ce que le champ `confrontation` d'un modèle annonce a été
  fait, au moins pour une part qu'il dit — ses valeurs ou ses règles, à la
  date où il dit appliquer le droit, mises en regard de celles du dépôt, et
  l'issue écrite, accord ou écart tranché. Une lecture qui ne met ses règles
  qu'en regard du droit d'aujourd'hui, quand elles sont d'une autre date, ne
  confronte rien.
- *Neuf l'avaient été, ou le sont ce jour,* et leur ligne nomme désormais la
  version confrontée :
  - EDIFIS (`95ef983`) : ses taux de vieillesse du régime général de 2015 à
    2025, les quatre, sont ceux du dépôt, année par année
    (`taux_cotisation_annuels.csv`). Le 5 octobre, on l'avait vu par D. 242-4,
    que tous deux suivent, pour 2017 à 2026 ; 2015 et 2016, ce jour. Son bilan
    disait encore le dépôt aux moyennes de période de sa fiche, que le relevé
    du 4 octobre avait lues : corrigé. Reste l'Agirc-Arrco.
  - Saphir (`7bc72c9`) : ses seuils de CSG de 2017 pour une part (le 19
    octobre, action 89) ; l'abattement des pensions de son impôt de 2016, 379
    et 3 711 €, celui du dépôt pour les revenus de 2015 (ce jour).
  - `ir-catala` (`7f5fe83`) : son abattement des pensions, qu'il n'écrit que
    « sous condition année_revenus = 2022 », est celui du dépôt pour ces
    revenus, 4 123 et 422 € (`impot_revenu.yaml`). Son écart au registre le
    disait faux contre les montants de 2025 : c'est un retard, récrit tel.
  - EUROMOD (J2.54+) : ses seuils de CSG de 2026 et leurs majorations par
    demi-part, le 4 octobre (la fiche `csg_des_pensions_selon_le_revenu`).
  - Retraites 2027 d'A. Tilloy (`431dd9f`) : il calcule 2027 sur des
    paramètres indexés, que rien ne fixe encore ; ceux de 2026 qu'il cite
    (`params.js:52-64`) sont ceux du dépôt — les seuils de CSG à une et à deux
    parts, la décote et l'abattement des personnes âgées des revenus de 2025
    —, sauf la deuxième borne du barème, son erreur déjà au registre.
  - Le simulateur d'Aurain (`59b7985`) : ses âges et ses durées du droit en
    vigueur, aux bornes de naissance du texte, sont ceux du dépôt, lus ce
    jour dans `baselines_retraites.yaml` ; ses majorations de CSG et son
    abattement aussi. Sa tête a avancé (`8b7dd75`), non relue.
  - « Quand pourrai-je partir » (`94616bc`, `outil.js` inchangé à la tête du
    jour, `946b108`) : sur tout son curseur, de 1961 à 2010 (`index.html`),
    ses âges et ses durées du droit en vigueur sont ceux du dépôt, sauf 1961,
    l'écart déclaré ; pour 1965, il retient les nés d'avril à décembre, la
    majorité, comme il le dit. Avant ce jour, seul 1961 était écrit.
  - devcrafting (`2312ebd`) et le tableur de vérification (`5344b10`) : leur
    `confrontation` disait « un calcul à relire », et la relecture du 1er et
    du 4 octobre les a mis règle par règle en regard du dépôt — raison pour le
    premier sur la première tranche du RCI, le taux des artisans au-dessus du
    plafond et le 1 % maladie de la complémentaire, pour le second sur le
    seuil d'avant 1972, tous repris (138.18, 138.2, 138.6) ; tort ailleurs.
- *Quatre ne l'ont jamais été,* et leur `confrontation` le dit, avec ce qui
  reste : modele-as (le calcul à rejouer sur des revenus de dirigeant ; de la
  famille de l'Urssaf, dont modele-social et modele-ti sont confrontés, son
  accord ne compterait qu'une fois) ; Catala (ses règles de retraite, mises
  en regard du seul droit en vigueur, qu'elles précèdent : restent ses âges
  de 2023 pour les générations parties sous cette loi, jusqu'à 1963, l'âge du
  taux plein, l'inaptitude, l'ASPA jusqu'en 2020) ; le simulateur de SUD
  éducation (le calcul au droit de 2020, jamais rejoué ; ses durées et son
  point, périmés aujourd'hui, sont ceux de 2020) ; Nos Retraites (un projet
  de loi, et le droit d'avant 2023, seul comparable).
- *Ce que les tests tiennent* (`tests/test_referents.py`) : les valeurs lues
  chez EDIFIS, Saphir, `ir-catala`, EUROMOD, Tilloy, Aurain et « Quand
  pourrai-je partir », contre la donnée du dépôt qui dit la même règle — une
  donnée qui change remet leur accord en question, et leur ligne se relit ;
  l'écart de 1961 ; la version que leur ligne doit nommer, vue rouge avant le
  registre. Et le tableau de bord, dont la phrase « 24 ont déjà été
  confrontés…, et 213 écarts y ont été trouvés » prêtait à ces 24 tous les
  écarts du registre : « le registre compte 213 écarts, dont 170 chez eux »
  (`scripts/tableau_de_bord.py`, le test vu rouge d'abord).
- *Le tableau de bord, après* : 24 modèles confrontés ou qui donnent des
  valeurs, et 4 à confronter en premier, dans l'ordre du registre :
  `modele_as`, `catala`, `simulateur_sud_education`, `nosretraites_cas_types`.

**Ce qui reste.** Le premier modèle qui reste à confronter, dans l'ordre du
registre, est modele-as : rejouer son calcul, le paquet npm sous MIT, sur une
grille de revenus de dirigeant de 2024 à 2026, et comparer ses trimestres et
ses points Agirc-Arrco à ceux du dépôt, comme pour modele-ti. Puis Catala,
le premier hors de toute famille. Restent aussi, des modèles confrontés en
partie : l'Agirc-Arrco d'EDIFIS (tranches 1 et 2, CET) ; l'abattement de
2017, celui des personnes âgées et l'ASPA de 2017 de Saphir ; le quotient
familial des retraités d'`ir-catala` ; les systèmes FR_2015 à FR_2025
d'EUROMOD ; les bornes de carrière longue d'Aurain. Au propriétaire, rien à
trancher.

*Fichiers.* Le registre, `tests/test_referents.py`,
`scripts/tableau_de_bord.py`, `docs/etat.md`, la feuille de route et cette
note. Ni fiche, ni règle, ni page : aucune entrée au journal de veille.
