# Les deux parcours d'Union Retraite : lus sans une saisie, quatre exemples, deux écarts de la retraite progressive

**Le 19 octobre 2026 : deux lignes réservées (cd55c55), puis lues.** Ce sont
celles par lesquelles le bloc « Reprise » disait de commencer,
`union_retraite_progressive` et `union_retraite_expatriation`, sur
parcours.info-retraite.fr, que la recette `chaine_incomplete` rend joignable.
Elles passent à `explore`, et de `simulateur` à `regle` : ce sont des
parcours d'information, qui ne calculent rien, et tout leur arbre —
questions, réponses, enchaînements — est dans la page, un JSON
(`_rawDataParcours`), lu en deux requêtes. Aucune saisie : la voie 2 du § 3.5,
et l'accord du propriétaire qu'elle exige, n'avaient pas lieu d'être. Les deux
`a_en_tirer` datent du 22 septembre ; le modèle sert depuis la retraite
progressive (29 septembre) et les carrières hors de France (1er octobre), et
c'est contre lui que les parcours ont été lus.

- *La retraite progressive* (quinze questions, vingt-cinq réponses) concorde
  avec la fiche `retraite_progressive` : soixante ans pour les retraites
  progressives prenant effet depuis le 1er septembre 2025, fonctionnaires de
  toutes catégories compris ; 150 trimestres « toutes activités confondues » ;
  40 à 80 % du temps de travail, 50 à 90 % pour un fonctionnaire ; la
  fraction, complément à 100 % de la quotité (80 % donnent 20 %, 65 % donnent
  35 %, seuls chiffres du parcours, sans montant) ; la CRPCEN et la CNIEG
  l'ouvrent depuis 2023, la CRPN non, qui a son temps alterné. Deux écarts
  neufs, lus dans l'index LEGI (à jour au 18 octobre) et déclarés dans la fiche
  et dans `docs/limites/ecarts-au-droit-positif.md`, sans être codés :
  - du libéral, le parcours dit qu'« une demande effectuée en mars 2026 ne
    pourra pas prendre effet avant le 1er janvier 2027 ». C'est D. 161-2-24-2,
    depuis le 1er septembre 2023, pour tous les non-salariés du 2° de
    L. 161-22-1-5 ; s'y ajoutent les dix-huit mois à 50 % « à titre
    provisionnel » (D. 161-2-24-3, II, depuis 2026) et le revenu d'au moins
    40 % du SMIC (D. 161-2-24-1). Le modèle sert la fraction à la date
    déclarée ;
  - la caisse de la SNCF l'ouvre depuis 2023, dit le parcours, quand la fiche
    disait non relus les décrets propres des régimes spéciaux. Ils le sont :
    SNCF (décret n° 2008-639, article 6 bis, depuis le 22 octobre 2023), RATP
    (décret n° 2008-637, article 22 bis) et Banque de France (annexe au décret
    n° 2007-262, article 35 bis, la pension partielle du code des pensions
    civiles), depuis le 1er septembre 2023. Le modèle la refuse à leurs agents
    (motif `regimes`, essayé sur un agent né en 1963 qui la demande à 61 ans).
    La Comédie-Française, sans affiliation au modèle, liquide sans la
    cessation d'activité qu'elle exige d'ordinaire (décret n° 68-960,
    article 26). L'index ne dit rien des marins ;
  - hors du modèle, sans rien changer : les VRP et les artisans taxis de
    l'assurance volontaire, exclus ; la cotisation sur un temps plein, que les
    limites disent déjà (« ne surcotise pas ») ; le plan de cession des
    exploitants agricoles.
- *L'expatriation* (cinquante questions, quatre-vingt-quinze réponses, et le
  lexique) concorde avec le tableau des accords. Les quarante-deux
  territoires conventionnés du lexique sont les trente-sept conventions en
  vigueur, Madagascar, sans coordination vieillesse, que le tableau écarte,
  et les quatre collectivités qui ont leur régime ; les dix-sept États qui
  couvrent les indépendants, les quatorze conventions
  `salaries_et_non_salaries` et trois de ces collectivités ; les sept accords
  qui totalisent un État tiers, les sept qui en ont la liste (les brochures
  de 2020 en nommaient six, sans la Serbie, dont l'accord date au tableau du
  1er décembre 2023). Les dix-huit brochures, de 2019 et 2020, typent les
  conventions : les trente-sept en vigueur au 1er janvier 2020 ont toutes le
  `calcul` de leur type. La fiche `totalisation_des_periodes_etrangeres`
  porte la lecture.
  - *Quatre exemples des brochures* entrent au témoin et concordent :
    Jean, né en 1956, 156 trimestres en France et 12 en Espagne, au taux plein
    par la totalisation, salarié, puis artisan avec la Finlande ; Jean et
    Yves, clercs de notaire nés en 1959, au calcul national de la CRPCEN, 75 %
    moins 1,25 % par trimestre manquant, dix et seize. Yves part « dès
    61 ans » : un mois plus tard, l'âge d'annulation de 2020, 65 ans, ne laisse
    que quinze trimestres de décote, et le témoin le fait partir le mois même.
    Né un 1er, il n'en aurait que quinze aussi : la garde des présomptions de
    GitHub l'a montré le jour même, et les deux clercs naissent désormais le
    15 mars 1959, date entière, la brochure ne disant que l'année.
    Ne se rejouent pas : le prorata des salariés, la note des brochures
    réduisant les vingt-cinq années quand le régime étranger est équivalent,
    ce que l'Espagne est ; Yves salarié avec le Québec, ses 37,5 ans en France
    ne faisant pas 150 trimestres au régime général, qui valide par année ; la
    pension européenne de la CRPCEN, que les brochures écrivent « Taux de la
    retraite (70,48%) X (156/166) », quand 70,48 % vaut déjà 75 % × 156/166,
    et que le modèle ne calcule pas, un régime spécial n'y comptant pas les
    périodes étrangères (approximation déclarée).
  - *Deux pistes* vont à la fiche, pour une session du modèle : « soit les
    périodes EEE, soit les périodes suisses », disent parcours et brochures,
    quand l'instruction ministérielle 2002/5, que la Cnav diffuse le 10 juillet
    2002, totalise ensemble les États membres et la Suisse ; la règle ne
    viserait que l'Islande, le Liechtenstein et la Norvège, que le tableau
    range avec la Suisse sous un seul instrument. Et le recalcul de la pension
    française quand l'autre État liquide, avec une surcote tirée des périodes
    italiennes (l'exemple d'Aline), que le modèle ne fait pas.
  - *Pour la session de D. 351-1-2 (138.14)* : le volontariat international
    compte, dit le parcours, 90 jours pour un trimestre et, à la carrière
    longue, quatre trimestres au plus ; L. 122-15 du code du service national
    l'assimile, s'il dure six mois, à une période d'assurance du premier
    régime de base où le volontaire s'affilie ensuite (LEGIARTI000021960477,
    depuis le 1er juillet 2010 ; LEGIARTI000051289102, depuis 2026). Le dépôt
    n'en dit rien ; la fiche `carriere_longue_reputes_cotises_autres` porte
    le service national de D. 351-1-2, 1°, et n'est pas touchée ici.
  - Défauts du parcours, sans effet : son lexique omet l'Islande de l'EEE,
    que les brochures portaient ; son exemple « France, Espagne, Suisse »
    contredit l'instruction de 2002.
- *Ce qui attend le propriétaire* : rien de neuf.
- *Le lot suivant* trouvera seize lignes `a_explorer` : neuf modèles du
  registre, dans les zones de 138.3, 138.5, 138.7 et 153 ; F33841 (138.12) ;
  le simulateur du COR, fermé ; cinq qui attendent le propriétaire (le lot
  des simulateurs, Légifrance, Gallica).
- *Fichiers.* `data/sources_a_explorer.yaml`,
  `tests/temoins/exemples_officiels.yaml`, les fiches `retraite_progressive`
  et `totalisation_des_periodes_etrangeres`, `data/reference/textes/perimetre.yaml`
  (le cliquet à 9 646), `docs/limites/ecarts-au-droit-positif.md`,
  `docs/limites/3-systeme-actuel.md` (le compte des exemples, à 204), le
  journal de veille et cette note. Aucune règle du scénario 1 n'a bougé.
