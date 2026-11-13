# Relecture de `asv_medecins_points`, et ce qui attend le propriétaire sur l'action 130

Le 13 novembre 2026 (action 130, sur Fable 5.2). Relecture indépendante, contre les sources,
de la fiche `asv_medecins_points` telle que la note `2026-11-06-e16-asv-medecins-points.md`
l'a laissée. Ni règle, ni donnée, ni fiche, ni test n'est modifié : les écarts repartent à
l'étape suivante. Le modèle et son portage sont à une autre session (action 161) pendant
cette vague.

**Méthode.** Index de la DILA récupérés ce jour : JORF et LEGI à jour du 11 novembre 2026.
Chaque identifiant de la fiche retrouvé dans LEGI, sa date comparée ; chaque citation
comparée par script au texte de l'index (espaces normalisés, coupée aux « […] ») ; les sept
rédactions de l'article 2 du décret n° 72-968, les trois de ses articles 3 et 7, les sept de
son article 6, l'article 7 du décret n° 71-542, les articles 1er à 5 du décret n° 2011-1644,
D. 645-2 et D. 645-3 de 1985 à 2012, L. 645-2 et L. 645-5, lus en entier ; au JORF, les
décrets nos 72-968, 81-274, 85-205, 94-564 et 99-237. Les cas posés rejoués par
`servi_et_refait` (`tests/outils_pont.py`) : le portage sert, le moteur Python refait.

## 1. Ce qui est conforme

- Les 67 identifiants sont dans l'index, aux dates que la fiche leur donne ; les citations
  des textes, mot pour mot ; 21 des 22 fragments cités dans la prose aussi.
- Les points : 37,52, 30,16 et 27, au prorata des trimestres (article 2, toutes rédactions
  depuis le 8 juillet 1994 ; décret n° 94-564, article 3, JORFARTI000002368446).
- Les valeurs de service de l'article 4 du décret n° 2011-1644, dans ses six rédactions ; les
  forfaits de son article 1er ; les taux d'ajustement de son article 2 ; 102 F du 28 mars
  1999 (décret n° 99-237, article 2, JORFARTI000001044480) au 1er janvier 2012.
- La durée minimale : dix ans (décret n° 71-542, article 7), un an depuis le 15 février 1985
  (décret n° 85-205, JORFTEXT000000520378 : « PENDANT UNE DUREE MINIMUM D'UN AN »).
- **Les deux erreurs déclarées se retrouvent au centime**, par la requête du site (statut
  `medecin_liberal`, salaire 1, début à 30 ans, pension à 65 ans, profil par défaut) :
  nés en janvier 1937, 1940, 1950, 1953 et 1959, 879,52 points à 13,313333 €, 960,52 à
  14,133314 €, 994,46 à 13,184592 €, 998,37 à 11,518896 €, 1 014,99 à 11,944317 € ; et
  l'exercice de neuf mois (né en janvier 1960, `metier2_debut` 40, `metier3_debut` 40.75) :
  27 points × 11,82 € × 1,15 = 367,01 €. Sous le profil « plat », les trois derniers cas ont
  moins de points (992,96, 993,03, 1 001,73) : la fiche ne dit pas le profil.

## 2. Les écarts

**(a) La cotisation d'avant 2012 est portée au tiers — erreur neuve, non déclarée.**
D. 645-2 fixe « la cotisation annuelle des bénéficiaires » : « pour les médecins, à trente
fois la valeur […] du tarif de la consultation », puis cinquante-deux et soixante fois ;
D. 645-3, celle des caisses « au double de la cotisation des bénéficiaires ». L. 645-2 de
1985 le dit de même (« une cotisation des bénéficiaires », « une cotisation annuelle du
régime général d'assurance maladie »), et l'article 6 du décret n° 72-968 : « la cotisation
des médecins conventionnés est fixée à trente et une fois la valeur ». Le médecin paie donc
N consultations, les caisses 2 N. La fiche du régime (`regimes/asv_conventionnes.yaml`)
prend N consultations pour le total et en donne le tiers au médecin : « 2 250 F, un tiers
pour le médecin, 114,34 € » en 1985, « 1 200 € par an, 400 € pour le médecin » en 2004 ; la
fiche de règle le répète (approximations 1 et 2). Recoupement : 60 × 23 € = 1 380 € en 2011,
ce que la presse donne au secteur 1, et 4 140 € au secteur 2 ; le mémento 2012 de la CARMF,
1 433 € et 4 300 €, que le modèle porte bien (1 433,33 €). Le modèle passe ainsi de 400 € de
2004 à 1 433 € en 2012, saut que les textes n'ont pas. À la main, pour 2004 : le texte,
1 200 € du médecin et 2 400 € des caisses ; le modèle, 400 € et 800 € : **2 400 € par an de
cotisation en moins au compte**, en euros de 2004. Aucun effet sur la pension du scénario 1,
dont les points ne dépendent pas de la cotisation ; le compte notionnel du médecin, lui,
reçoit le tiers de ses cotisations de l'ASV de 1972 à 2011.

**(b) L'article 6 du décret n° 72-968 n'est pas lu** (sept rédactions, LEGIARTI000006765951
à 957, qu'aucune fiche ne cite). Il décide de la cotisation appelée : « à concurrence de 75
p. 100 » du 1er juillet 1981 à 1992 (60 % avant, décret n° 81-274), sauf 1988 (« trente et
une fois », à 100 %), 1990 (« 33 fois ») et 1992 (« majorée de dix fois ») ; 100 % depuis
1993, année fixée à « 43,333 2 fois ».

**(c) La cotisation de 1994.** La fiche écrit « quarante-cinq fois la consultation en 1994,
cinquante-deux fois en 1995 — le décret n° 95-442 qui le portait a été annulé ». Le texte :
« A compter du 1er janvier 1994 […] les termes : << trente fois >> sont remplacés par les
termes : << cinquante-deux fois >> » (décret n° 94-564, article 1er, II,
JORFARTI000001585515 ; LEGIARTI000006738374, que la fiche nomme elle-même). Quarante-cinq
fois ne vaut que du 30 mars 1993 au 1er janvier 1994 (décret n° 93-763, abrogé par
l'article 4 du décret n° 94-564). Le décret n° 95-442 ne change, à D. 645-2, que les
chirurgiens-dentistes (« treize » devient « 46,33 »). La fiche du régime tient 1994 à
quarante-cinq fois partagées par moitié : faux sur les deux points, les caisses payant le
double depuis le 8 juillet 1994.

**(d) Avant le code.** « jusqu'en 1985, un arrêté que l'index ne porte pas » : la cotisation
était à l'article 1er, a, du décret n° 71-544, que l'article 2 de 1981 nomme, et le JORF en
porte le résumé (décret n° 81-274, JORFTEXT000000685106) : « TRENTE FOIS LA VALEUR AU 1
JANVIER DE L'ANNEE EN COURS DU TARIF DE LA CONSULTATION », 1055 fois la consultation pour
les prestations « LIQUIDEES AVEC UNE DATE D'EFFET POSTERIEURE AU 31-12-1980 », l'appel « DE
75% AU LIEU DE 60% ». Le résumé du décret n° 72-968 (JORFTEXT000000304093) : « ART. 2:
PRESTATION SUPPLEMENTAIRE ANNUELLE APRES 35 ANNEES DE COTISATIONS ». Les décrets nos 72-969,
75-892 et 78-282 modifient l'article 1er du décret n° 71-544, au titre seul. Ce qui reste au
fac-similé est donc un décret, non un arrêté.

**(e) D. 645-3 s'arrête le 2 décembre 2004** (LEGIARTI000006738169). « les caisses paient le
double […] depuis le 8 juillet 1994 (D. 645-3) » ne tient que jusque-là ; de 2005 à 2011, la
part des caisses a une autre source, non lue (la convention médicale). La fiche du régime
cite pourtant cet article pour 2004 à 2011.

**(f) L'erreur de la valeur de service oublie 2026.** La fiche nomme les liquidations « de
2013 à 2016, de 2018 à 2020, de 2024 ». Né en janvier 1961, pension à 65 ans en 2026 : le
modèle sert 1 020,52 points × 12,02685 € × 1,15 ; le texte, « 11,82 euros à compter de
l'exercice 2025 », sans rédaction plus récente à l'index du 11 novembre 2026 :
1 020,52 × 0,20685 × 1,15 = **242,76 € par an de trop**, l'année que le site sert le plus.
Au premier semestre 2012, à l'inverse, le modèle sert 13 € (né en janvier 1947) quand le
texte donne 15,55 € pour ce semestre.

**(g) Écarts faibles.**
- La citation de la version de 2026 : « ne peut obtenir aucun nouveau droit » ; le texte,
  « qui ne peuvent obtenir aucun nouveau droit ».
- La valeur de service « pour les pensions liquidées avant 2006 » vaut aussi pour les points
  liquidés de 2006 à 2010 (article 4, II, 1°), que la fiche ne nomme pas.
- 102 F font 15,5498 € ; le décret n° 2011-1644 écrit 15,55 €. À 15,55 €, les cas de 2002 et
  de 2005 donnent 1 967,20 € et 1 360,76 € au lieu de 1 967,02 € et 1 360,56 €.
- `nee_de` de la version `vingt_sept_points` nomme D. 645-2 ; les 27 points naissent de
  l'article 3 du décret n° 94-564.
- Le décompte des trimestres : six mois dans une année civile donnent 27 points, trois mois
  aucun, six mois à cheval sur deux années aucun. L'article 2 les veut « au prorata du
  nombre de trimestres cotisés », l'article 3 du trimestre civil suivant. Non chiffré.

**Conséquence.** La fiche reste hors de `LUES_AU_DROIT`. À reprendre par l'étape suivante,
dans la fiche et, quand le modèle sera libre, dans la fiche du régime : (a) à (f).

## 3. Ce qui attend le propriétaire, exposé le 13 novembre

Exposé dans la session, par caisse, les plus lourdes d'abord. Recommandation générale :
corriger le modèle là où le texte est clair, dire la limite là où il se lit de deux façons.
**Aucune réponse à l'heure de cette note** ; aucune correction ne s'ouvre avant elle, ni
tant que l'action 161 tient le modèle. Montants par an, aux cas posés des notes.

| Caisse | Le modèle | Le texte | Écart | Recommandé |
|---|---|---|---|---|
| CAVOM | minore l'inapte à 62 ans (2016-2024) ; lui refuse 62 ans depuis 2025 | sans minoration ; ouverte à 62 ans | 4 521,49 € en moins ; six mois, 8 317,99 € | corriger |
| CPRN | né en 1961, parti en 2023 : servi en avril 2025 | ouvert le 1er janvier 2024, plus minoré | quinze mois, 16 999,67 €, puis 1 079,34 € de trop | corriger |
| CARCDSF | pas de réversion ; les deux premières années comptées ; cinq écarts de points | réversion à 60 % ; dispense sans points depuis juillet 2026 | 4 147,36 et 5 654,21 € ; 1 528,23 € de trop | corriger |
| CARMF | points aux deux premières années et passé 75 ans | dispensés sans points depuis juillet 2026 | 2 284,25 € et au moins 300,22 € de trop | corriger |
| CARMF | pension au premier du mois | au trimestre civil depuis juillet 2026 | 1 171,35 ou 2 337,68 €, une fois | corriger, avec la CAVOM, la CARPIMKO et la CAVP |
| CARMF et ASV | 62 ans de janvier à mars 2017 ; un trimestre de trop pour qui naît un premier jour de trimestre | l'âge légal ; un trimestre de moins | 679,34 € en moins (ASV 873,34 €) ; 99,89 € de trop (119,42 €) | corriger |
| ASV | valeur du point portée aux prix ; moins d'un an d'exercice servi | valeur fixée par décret ; un an au moins | 1 967,02 € en moins (2002), 273,50 € de trop (2024), 242,76 € (2026) ; 367,01 € de trop | corriger |
| CAVAMAC | pas de majoration au second semestre 2011 ; quatre autres écarts | statuts de 2011 | 1 332,33 € en moins | corriger |
| CAVP | carrière longue depuis 2024, mauvaise pente ; pension au mois | 1,25 % par trimestre ; trimestre civil | 544,94 € en moins ou 1 410,68 € de trop ; 1 212,41 €, une fois | corriger |
| Cipav | le report majore tous les points ; aucun de 2008 à 2012 | ceux des trente premières années | au moins 549,19 €, 537,96 € et 152,05 € de trop ; au moins 215,43 € en moins | corriger, au décompte le plus favorable |
| CARPIMKO | rien de majoré d'octobre à décembre 2015 ; trois écarts | majoration due | au moins 397,36 € en moins ; 28,57 €, 136,90 €, 475,50 € une fois | corriger |

Non tranchés, à déclarer en limite : la Cipav en 2007 (0 ou de 136,19 à 347,40 €) et ses
anciens de la caisse des géomètres (0 ou 229,15 €) ; la CAVEC avant mars 2008 (2 741,17 € de
trop ou 2 398,21 € en moins) et son cumulant d'un salariat (de 0 à 3 056,14 €) ; quatre à
la CARMF, dont l'ASV d'avant 2017 (776,66 €) ; d'autres à la CPRN, la CAVP, la CARPIMKO et
la CAVOM. Deux questions de forme : la CRPNPAC, que le modèle refuse avant 50 ans quand les
textes l'ouvraient dès 45 ans avec vingt-cinq annuités, et ses vingt annuités (recommandé :
l'ouvrir comme le texte) ; la fiche du décret n° 2026-418 (recommandé : une sorte « fiche
de texte » au contrat). Les neuf questions du 3 novembre restent sans réponse consignée.

Comptes que le relevé n'a pas retrouvés tels que l'ancien bloc les annonçait : la CAVAMAC
(cinq écarts ou six), la CPRN (trois non-tranchés, non deux), la CAVP (trois ou quatre),
l'ASV (trois erreurs avec la durée minimale).

## 4. L'ancien bloc « Reprise », du 6 novembre, gardé en entier

Récrit ce jour à 150 mots (`.claude/rules/documentation.md`) ; le voici tel qu'il était.

> Reprise, au 6 novembre 2026. Fait : phases 0 à 8, cinq domaines clos, le sixième aux étapes 1 à 6 ; vagues 6 et 7 relues conformes (Agirc-Arrco 5cf7bbc, Agirc 18a4dc3, base des
> libéraux 5f19af8, L-bis 9fcd8a1, L-ter f6012e5, Ircantec d'avant 1983 cc627e8) ; les retouches de R-E, R-M3-ter, R-L-ter et R-D-bis (7e44534). Le 5 : la CRPNPAC à son âge (N 1464c06,
> R-N 329db34, b47aaf9 ; au propriétaire, le refus avant 50 ans, les vingt annuités et leur barème de 2012 à 2019) ; la CAVOM, la CARPIMKO et la CPRN à leur âge, sans la base, la CAVP à
> celui de la base (N ddc92fc, R-N2 10eb393, N-bis 0ba2aea). Lues au droit : la CAVAMAC, la CARCDSF, la CAVOM, la CARPIMKO, la CAVP, la CPRN, la CARMF, la Cipav, la majoration pour enfants des trois sections
> (E2 à E8 et leurs relectures) ; le décret n° 2026-418, lu au droit par E10 (relecture de E9 : R-E10 e1053a3) : la fiche, un texte et non un dispositif, rapporte chacun de ses 31 articles à la fiche de sa règle, et reste hors de `LUES_AU_DROIT` (au propriétaire : la forme d'une fiche de texte) ; `surcote_par_age_seul` lue au droit, ses sept régimes écrits en dix-huit versions, et entrée à `LUES_AU_DROIT` (E12 à E14) ; E14 a repris les écarts de R-E14 (les douze arrêtés qui modifient au JO les statuts de 1979 de la Cipav, l'article 17 par ceux de mai 1981, juin 1985, mars 1987 et juillet 2003, peut-être de mai 1982 et août 1987 ; l'arrêté du 21 septembre 2026 ; le cas posé de la CARPIMKO) et coupé les versions aux dates de la CAVEC, de la CAVP et de la CPRN ; E15 a repris les écarts de R-E15 (les six arrêtés de la CAVEC de 1980 à 2003, et dix de 1961 à 1977, au titre seul ; l'article 3.14 d'avant 2008 non identifié) et lu au droit `cotisation_par_classes_liberales`, ses trois régimes écrits en quinze versions et entrée à `LUES_AU_DROIT` (la classe 3 de la CAVP, `decret_2026_418_liberaux`, et celle des notaires, sans fiche, n'y sont pas)  ; E16 a repris les neuf écarts de R-E16 (1994, 1957, six arrêtés, l'article 2-1 de la Cipav, le décret n° 77-313, le renvoi des notaires) et lu au droit `asv_medecins_points`, sans l'entrer à `LUES_AU_DROIT` (restent la rédaction de 1972 de l'article 2 et l'arrêté de 1972, la coupe des versions à la date de liquidation, les liquidations d'avant 1999) ; à relire d'abord : E16 (`130/2026-11-06-e16-asv-medecins-points.md`).
> Au propriétaire, erreurs déclarées, non corrigées : la Cipav, trois et un non-tranché (le report ne majore que les points des trente premières années, le modèle tous : au moins 549,19 € par an pour un an depuis le 1er juillet 2026, 537,96 € depuis 2023, 152,05 € de 2013 à 2022 ; de 2008 à 2012, il ne majore rien : au moins 215,43 € servis en moins, au moins 419,43 € sous les trois décomptes de la première année, sous la réserve des dispositions transitoires de 2006 ; en 2007, non tranché, 0 € ou de 136,19 à 347,40 € ; le décompte de l'article 3.6, ouvert ; avant 2007, question 22 ; l'article 2-1, les anciens de la caisse des géomètres majorés de 33 % de 2000 à 2006, non tranché : 0 ou 229,15 € par an) ; la CARMF, trois (les deux premières années d'exercice et le semestre des 75 ans, dispensés sans points depuis le 1er juillet 2026 :
> 2 284,25 € et au moins 300,22 € par an aux cas posés ; la pension au trimestre civil), et, avec l'ASV, deux neuves (de janvier à mars 2017, l'âge légal et non 62 ans : 679,34 € par an, l'ASV 873,34 €, au cas posé ; né le premier jour d'un trimestre, un trimestre de trop : 99,89 €, l'ASV 119,42 €), l'ASV seule deux de plus (la valeur de service portée aux prix entre ses ancres : 1 967,02 € par an en moins pour une liquidation de 2002, 273,50 € de trop en 2024 ; la durée minimale d'un an d'exercice non servie : 367,01 €), et quatre non-tranchés ; la CARCDSF, sept, et une neuve (la part proportionnelle des deux premières années, dispensée depuis le 1er juillet 2026 : 1 528,23 € par an) ; la CAVAMAC, une (1 332,33 € par an) et cinq ; la CPRN, une et deux ; la CAVP, deux et trois ; la CARPIMKO, trois, une neuve (d'octobre à décembre 2015, rien de majoré : au moins 397,36 € par an, 1 059,64 ou 1 125,86 € sous la lecture du modèle, sous la réserve de la date d'effet) et quatre (le trimestre du jour de l'âge, 0 ou 68,45 €) ; la CAVOM, trois et deux ; la CAVEC, deux non-tranchés neufs (avant le 2 mars 2008, le modèle majorant dès le 1er janvier : 2 741,17 € par an de trop, ou au plus 2 398,21 € en moins avant 2008, au cas posé ; depuis 2013, le cumulant d'un salariat, que le décret met en classe C au moins et le modèle sur son revenu libéral : 3 056,14 € par an servis en moins au cas posé, 2 507,32 € sans les années de classe A d'office, 1 151,68 € si le décret vaut jusqu'aux statuts de 2018, ou rien, les statuts de 2018 n'en faisant qu'une option) ;
> `…-11-03-decisions-du-proprietaire.md`. Au fac-similé ou au seul Bulletin officiel : des statuts de la CAVAMAC (1967), CAVEC (avant 2008), CARPV (avant 2014), CARPIMKO, CAVP (d'avant 2009 : arrêtés du 29 décembre 1948 et du 1er juin 1950), CPRN (2004), CAVOM, CARMF et Cipav (avant 2016) ; candidats non lancés : l'Agirc-Arrco de 1955 à 1983, les biologistes et la durée, le taux plein de 1977 et 1982, `ages_reference.csv`, les points de la CARPIMKO de 1956 à 2025, la minoration de la Cipav (article 5-1, 2°, du décret n° 79-262).

## Tests

`python -m pytest -m rapide` : 4 953 verts, 9 sautés. `tests/test_carte.py` et
`tests/test_donnees.py` : 168 verts. `tests/test_consignes.py`, `tests/test_prose.py` et
`tests/test_carte_du_depot.py`, qui tiennent le bloc « Reprise » et la prose : verts.
