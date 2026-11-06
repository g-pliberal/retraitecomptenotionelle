# Étape 4, thème « Allocation du minimum » : les exposés et leurs références

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 de 12 h 30 à 12 h 31 UTC, par les
  fonctions de `scripts/fetch/cnav_legislation.py` (`_obtenir`, `liens`,
  `liens_de_l_import`), sans écrire le registre : `/expose`, `/liste`, `/baremes`, les trois
  collections des fenêtres et `/mises-a-jour`, de l'import de la nuit (5 h 00 UTC), sans
  aucun lien du site SharePoint de la caisse. Les 17 exposés sont servis à la date que le
  registre porte, du 24 octobre 2025 au 16 juillet 2026. `python scripts/veille_droit.py` :
  rien de changé dans le thème (un exposé d'un autre, `prelevement_retraite_cotisation_
  assurance_maladie_ex.aspx`, a changé de date, encore à lire).
- *La lecture* : les 17 exposés, en entier, par cette session — les dix de l'allocation de
  solidarité aux personnes âgées (Aspa), puis les sept de l'allocation supplémentaire
  d'invalidité (ASI), dont quatre (résidence, ressources, évaluation des ressources,
  recouvrement) ont été lus ligne à ligne contre leur pendant de l'Aspa, qu'ils reprennent
  pour l'essentiel. Chacun confronté à la fiche `minimum_vieillesse` (son effet, ses
  approximations, ses séries `legislation/minimum_vieillesse.csv`,
  `minimum_vieillesse_couple.csv` et `minimum_vieillesse_avant_2007.csv`), à
  `residence_et_minimum_vieillesse`, à `inaptitude_au_travail`, à « Un ménage, un patrimoine,
  des ressources » (`docs/limites/ecarts-au-droit-positif.md`), et au code des deux moteurs :
  `foyer_et_net` (`src/retraite_notionnelle/droit/foyer.py`, ligne 211) et `foyerEtNet`
  (`moteur/js/droit/foyer.js`, ligne 197), `condition_de_residence` (ligne 135) et
  `conditionDeResidence` (ligne 116), `age_de_l_aspa` (`droit/invalidite.py`, lignes 154 à
  170) et `ageDeLAspa` (`moteur/js/droit/invalidite.js`, lignes 115 à 126),
  `MinimumVieillesse` (`scenarios/actuel.py`, ligne 1962, `AGE_OUVERTURE` ligne 1975 ;
  `moteur/js/regimes.js`, ligne 1335). Les textes, à l'index LEGI à jour au 2 novembre 2026 :
  L. 815-1 (rédactions du 16 octobre 2015, du 1er septembre 2023 et du 23 juillet 2026),
  R. 815-1 (du 3 juin 2011, du 1er janvier 2015 et du 1er septembre 2023), L. 351-8 (du
  22 janvier 2014, du 1er septembre 2023 et du 28 février 2025), L. 351-1-5, L. 815-7 (du
  1er janvier 2006 et du 1er janvier 2020), R. 815-3, L. 815-24, et l'article 37 de la loi
  n° 2014-40. Le cas du versement forfaitaire unique a été calculé par le portage
  (`Saisies`, `tests/outils_pont.py`).
- *Le rapprochement de l'index* (LEGI à jour au 2 novembre 2026, JORF au 3). Les exposés
  lient 171 fois Légifrance, vers 85 cibles : 84 identifiants et une adresse. 72 identifiants
  se trouvent à l'index, et chacun concorde avec son ancre par le numéro de l'article (65) ou
  du texte (7), à une réserve : dans l'exposé « Compétence - Aspa », « art. R815-3 » mène deux
  fois à R. 815-13 (LEGIARTI000006753606). Des 12 absents, neuf sont hors du champ social de
  l'index — l'article 2134 du code civil et le code civil lui-même, les articles 669, 764, 768
  et 775 du code général des impôts, L. 132-8 du code de l'action sociale et des familles,
  L. 132-11 et L. 132-13 du code des assurances — ; deux se trouvent par le numéro : la loi
  n° 2024-42 du 26 janvier 2024, dont l'index porte les articles (JORFARTI000049040254 et
  suivants), et le décret n° 82-307 (JORFTEXT000000701321, comme H9 l'a trouvé) ; reste
  LEGIARTI000006681337, que les deux exposés du recouvrement lient pour « Art. 146 du code de
  la famille et de l'aide sociale », et l'exposé « Compétence - Aspa » pour « Css art.
  L815-7 », quand l'index porte L. 815-7 sous ses propres identifiants (LEGIARTI000006744864,
  que le même exposé lie plus bas). L'adresse : celle, ELI, du décret n° 2019-1084
  (JORFTEXT000039281172, comme H8 l'a trouvé).
- *Les sorts*, sous la convention de la note du premier thème. 17 exposés : 16 `limite`, et
  1 `hors_modele`, la compétence de l'Aspa (l'organisme qui la sert : celui de l'avantage de
  base ; à plusieurs, les non-salariés agricoles, puis le régime général, puis l'avantage le
  plus élevé ; sinon le service de l'allocation). Les sept de l'ASI, prestation que le modèle
  ne sert pas, sont `limite`, renvoyés à la limite neuve, comme H8 et H9 l'ont fait des
  allocations avant retraite et des avantages de survivant. 4 fenêtres : 3 `limite` — les
  anciennes allocations du minimum (la fiche `minimum_vieillesse` et la limite), « Ce qui
  change au 01/09/2023 » (les fiches `minimum_vieillesse` et `residence_et_minimum_vieillesse`),
  le capital d'exploitation agricole que la succession ne compte pas (la fiche) — ; 1
  `hors_modele`, « Foyer », définition du lexique. 4 listes `limite`, lues en tête, leur sort
  ne tenant qu'à leur nature : les ressources exclues de l'Aspa, alphabétique et par nature
  (la fiche et la limite), et celles de l'ASI (la limite). Laissée `a_lire` avec son thème,
  « Accords internationaux et d'outre-mer » : la liste des pays de l'Espace économique
  européen, que lient les exposés de la résidence et de la régularité du séjour, comme l'ont
  laissée la note des majorations et H9. 6 avis `hors_modele`, comme les autres : 4 (les
  plafonds de l'ASI au 1er avril 2023), 48 (l'abattement des revenus professionnels, 2015),
  172 (le pouvoir de contrainte, 2017), 232 (l'ASI revalorisée au 1er avril 2019), 306 (ses
  plafonds au 1er avril 2025), 328 (ses plafonds au 1er janvier 2026).
- *Les références*, que leurs liens rangent, des exposés, fenêtres et listes rangés qui les
  lient, sans les barèmes ni les avis : 42 rangées, 38 `limite` — aux fiches et à la limite
  que portent ces objets — et 4 `hors_modele`, que ne lie que l'exposé de la compétence : les
  circulaires ministérielles du 21 septembre 1956 et 70/SS du 5 août 1957, les lettres Cnav
  du 28 octobre 1988 et du 6 septembre 1990. 71 déjà `limite` dont le renvoi s'étend
  (ci-dessous) ; 6 qui le portaient déjà. Les 9 `branche` restent telles : aucun objet rangé
  ici ne les lie. Restent `a_lire` les 78 que seuls lient des barèmes et des avis — les
  circulaires annuelles des montants, des plafonds, de la revalorisation et du SMIC —, comme
  les thèmes précédents ont laissé les leurs.
- *Les renvois qui s'étendent* (71 références), de ce qu'y ajoutent les objets qui les lient.
  La fiche `minimum_vieillesse` seule (56) : circulaires Cnav 13/74, 102/84, 31/85, 49/86, 77/86, 69/88, 84/88, 73/89, 50/99, 2001/72,
  2005/14, 2006/6 (que la base nomme sans la servir), 2009/48, 2012/43, 2014/29, 2015/13,
  2016/33, 2020/8, 2021/24, 2023/21, circulaire Fnoss A 146 ter/264 du 26 septembre 1956,
  circulaires ministérielles 85/SS du 27 juillet 1956, 59/SS du 7 juillet 1958, 98/SS du
  22 octobre 1959, 71/SS du 27 mai 1963, 64/SS du 22 juin 1964, R. 815-22 du code de la
  sécurité sociale, Cour de cassation du 23 janvier 1974 et du 18 mai 1977, diffusion des
  instructions ministérielles 2013/8, lettres Cnav du 14 juin 1973, du 21 décembre 1977, des
  16 avril et 21 mai 1997, du 5 décembre 2002, du 6 mai 2003, lettre de la Fnoss du 4 août
  1964, lettres ministérielles du 3 août 1959, du 5 janvier 1962, 3536/AG du 23 mai 1962,
  GA/1838 du 29 octobre 1962, 261/258 du 20 décembre 1962, 119/105 du 27 février 1963,
  180/189 du 9 août 1963, 6728/AG du 7 juillet 1966, 7053/P du 28 avril 1971, 558 G/79 du
  19 mars 1982, du 13 avril 1984, 66 AG/85 du 20 août 1985, AG 216/89 du 7 juillet 1989, du
  21 novembre 1994, du 14 octobre 2002, du 23 octobre 2009, réponses à des questions écrites
  des 29 avril et 29 juin 1976 et du 31 janvier 1983. Les fiches `minimum_vieillesse`,
  `inaptitude_au_travail`, `residence_et_minimum_vieillesse` et la limite (3) : circulaires
  Cnav 2023/14, 2024/29, ministérielle 21/SS du 21 mai 1976. Les trois fiches (4) :
  circulaires Cnav 60/96, 2018/24, 2019/13, 2022/8. `minimum_vieillesse` et
  `residence_et_minimum_vieillesse` (2) : circulaires Cnav 2007/15, 2025/22. Ces deux fiches et
  la limite (1) : circulaire Cnav 2023/22. `minimum_vieillesse` et la limite (2) : circulaire
  Cnav 2015/60, lettre Cnav du 19 octobre 1993. `inaptitude_au_travail` (2) : circulaires Cnav
  2006/66 et 2018/18. La limite (1) : circulaire Cnav 82/74.
- *La limite* « allocations du minimum » (`docs/limites/3-systeme-actuel.md`), neuve : le
  modèle sert l'Aspa et, avant 2007, les deux étages ; ni l'ASI, ni les autres anciennes
  allocations du minimum ; de l'Aspa, il ne lit pas l'âge abaissé des retraites anticipées, le
  plafond de la veuve de guerre, celui des époux séparés, les ressources hors des pensions, la
  subsidiarité, l'aide aux anciens migrants, les versements exceptionnels de 2008 et 2009, la
  récupération sur la succession.

**Ce que la lecture a trouvé, sans écart.** Ce que la fiche `minimum_vieillesse` et
`foyer_et_net` portent déjà : l'allocation différentielle sous le plafond du foyer ; un seul
allocataire du couple au montant d'une personne seule, deux au montant du couple par moitié
(exposé « Montant - Aspa » : « Dès lors qu'une seule allocation est servie, le montant d'Aspa
retenu est le montant "personne seule" » ; « La moitié du dépassement de ressources est déduite
de la moitié du montant d'Aspa "couple" ») ; le barème du couple que donne l'ASI du conjoint,
déclaré ; les ressources de trois ou douze mois, l'abattement des revenus d'activité depuis
2015 et les biens, déclarés ; la récupération sur la succession, déclarée. Ce que porte
`residence_et_minimum_vieillesse` : six mois de séjour, neuf depuis le 1er septembre 2023, la
tolérance des cent soixante jours, que la fiche cite de l'exposé « Condition de résidence -
Aspa », le foyer permanent, le séjour régulier de dix ans (L. 816-1), déclarés. La retraite
progressive : « L'attribution d'une retraite progressive entraîne la suspension de l'Aspa au
point de départ de la retraite progressive » (exposé « Montant - Aspa ») ; le modèle ne sert
l'allocation qu'aux liquidations, où l'échéancier appelle `foyer_et_net` et `foyerEtNet`
(`src/retraite_notionnelle/echeancier.py`, lignes 551 et 598 ; `moteur/js/echeancier.js`,
lignes 604 et 657), jamais pendant la fraction. L'âge de l'inapte : « Cet âge est abaissé à
l'âge légal de départ en retraite au titre de l'inaptitude pour les personnes reconnues ou
réputées inaptes au travail » (« Conditions d'attribution - Aspa »), le paramètre `age_aspa`
de `inaptitude_au_travail`, soixante-deux ans depuis le 1er septembre 2023 (D. 351-1-14).
Ce que d'autres notes ont déjà déclaré, que ces exposés touchent : l'allocataire de l'AAH dit
réputé inapte, non tranché (G12) — l'exposé « Conditions d'attribution - Aspa » le nomme, avant
le 1er septembre 2023, parmi les titulaires d'une retraite anticipée de l'assuré handicapé qui
avaient l'Aspa à l'âge légal. La fenêtre « Ce qui change au 01/09/2023 » dit seule ce que les
exposés n'ont pas encore récrit : « Le droit est ouvert à 62 ans à : - l'assuré titulaire d'une
retraite anticipée carrière longue (RACL) ; - l'assuré titulaire d'une retraite anticipée assuré
handicapé. »

**Une approximation déclarée, à préciser, aux sessions du modèle** (rien n'a été corrigé) :
*l'âge de l'Aspa des retraites anticipées.* R. 815-1, rédaction du 1er septembre 2023
(LEGIARTI000047633276) : « L'âge mentionné à l'article L. 815-1 est fixé à soixante-cinq ans.
Il est abaissé à l'âge prévu à l'article L. 351-1-5 pour les personnes mentionnées aux 2° à 5°
de l'article L. 351-8. » L. 351-8, même date (LEGIARTI000047452736), compte parmi elles le
« 4° bis Les travailleurs handicapés admis à demander la liquidation de leur pension de
retraite avant l'âge prévu au premier alinéa de l'article L. 351-1 » et le « 4° ter Les
assurés dont l'âge mentionné au même premier alinéa est abaissé dans des conditions prévues à
l'article L. 351-1-1 », la carrière longue ; l'âge de L. 351-1-5 est soixante-deux ans
(D. 351-1-14, que lit `inaptitude_au_travail`). L'exposé et la fenêtre le disent (« les
titulaires d'une retraite anticipée carrière longue ouvrent droit à l'Aspa à 62 ans »). La
fiche `minimum_vieillesse` le déclare en termes généraux : « R. 815-1 ouvre l'allocation dès
l'âge de leur taux plein aux assurés des 2° à 5° de L. 351-8 ; le modèle ne la sert ainsi
qu'à l'inapte et à l'ancien invalide, à soixante-cinq ans aux autres », effet « non mesuré ;
léger », et ne nomme que les anciens combattants, les mères de famille ouvrières et les
travailleurs manuels. Deux choses sont à y préciser : R. 815-1 ne dit pas « l'âge de leur
taux plein » mais l'âge de L. 161-17-2 de 2011 à 2023, celui de L. 351-1-5 depuis ; et, depuis
le 1er septembre 2023, la carrière longue et le handicap y entrent. Les deux moteurs ne
baissent l'âge qu'à `reconnu_inapte` (`age_de_l_aspa`, `droit/invalidite.py`, lignes 165 à
170 ; `ageDeLAspa`, `moteur/js/droit/invalidite.js`, lignes 118 à 125). *Cas posé* : une
assurée née en 1964, partie en retraite anticipée pour carrière longue après le 1er septembre
2023, avant ses soixante-deux ans, seule, résidant en France, dont les pensions font 10 000 € par an en 2026, l'année de ses
soixante-deux ans. La caisse lui sert l'Aspa dès soixante-deux ans : 1 043,59 € par mois
(montant d'une personne seule en 2026, que la fiche porte) moins 10 000 / 12 = 833,33 €, soit
210,26 € par mois ; le modèle, rien jusqu'à soixante-cinq ans. Sur les trois années, aux
montants de 2026 : 210,26 × 36 = 7 569,36 € de moins au modèle. Seules les petites pensions
d'une retraite anticipée y entrent ; l'effet n'en est pas mesuré.

**Un point non tranché, sans candidat** : *le versement forfaitaire unique et l'Aspa.*
L'exposé « Conditions d'attribution - Aspa » : « La retraite personnelle payée en un versement
forfaitaire unique ne donne pas droit à l'Aspa » ; « Compétence - Aspa » : elle « n'est pas
attribuée avec […] le versement forfaitaire unique ». R. 815-3 (LEGIARTI000006753525) : « est
considérée comme avantage de vieillesse de base toute prestation viagère » ; L. 815-7
(rédaction de 2006, LEGIARTI000006744864) : « Pour les personnes qui ne relèvent d'aucun
régime de base obligatoire d'assurance vieillesse, l'organisme compétent est le service de
l'allocation de solidarité aux personnes âgées ». Le modèle garde dans les ressources la rente
que le versement remplace (« ``montant`` reste la rente qu'il remplace »,
`src/retraite_notionnelle/droit/commun.py`, lignes 85 et 86), et sert l'allocation. *Cas
calculé par le portage*, celui de `tests/test_versements_uniques.py` : née en 1950, deux
trimestres de 1970 (150 €), partie à soixante-cinq ans en 2015 ; sa pension du régime général,
93,18 € par an, et son allocation Arrco, 6,56 €, sont versées en capital (1 397,77 € et
111,47 €) ; le modèle lui sert l'allocation, 9 600 € par an en tout (`pension_annuelle`,
`minimum_applique`). Lue comme la caisse, sans organisme pour la servir —
elle relève du régime général —, elle n'a pas d'Aspa : 0 € par an, contre 9 600 €. Lue comme
une personne sans avantage de vieillesse, que le service de l'allocation prend, son capital
compté à 3 % (R. 815-25 ; « Toute somme qui a le caractère d'un capital entre dans le
patrimoine », « Evaluation des ressources - Aspa ») : (1 397,77 + 111,47) × 3 % = 45,28 €,
soit, au même plafond, 9 600 − 45,28 = 9 554,72 € par an, 45,28 € de moins qu'au modèle. Le texte ne tranche
pas qui relève « d'aucun régime » ; seules les pensions sous le seuil (154,09 € par an en
2012, 156,09 € en 2015) et prises avant 2016 y entrent.

**Ce que la base sert de travers.** Dans l'exposé « Compétence - Aspa », « art. R815-3 » mène
deux fois à R. 815-13, et « Css art. L815-7 », une fois, à l'identifiant que les exposés du
recouvrement donnent à l'article 146 du code de la famille et de l'aide sociale ;
« Circulaire Cnav 2007/15 du 15/02/2007 », trois fois, pour celle du 1er février 2007 ;
« Circulaire Cnav 2007/15 du 01/02//2007 » ; « Css art. art. R. 815-76 ». Les exposés de
l'évaluation des ressources, de l'Aspa comme de l'ASI, disent la donation « après
l'attribution de la retraite de réversion », reprise de l'exposé de la réversion. L'exposé
« Montant - ASI » annonce depuis 2020 un mode de calcul neuf (« Le décret 2020/1251 du
13/10/2020 prévoit un nouveau mode de calcul du montant de l'allocation supplémentaire
d'invalidité à compter du 01/04/2020 ») et décrit encore l'ancien.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et
la limite neuve. Les références prennent les renvois des exposés, fenêtres et listes rangés
qui les lient, sans ceux des barèmes, des avis, ni des fiches qui les citent par leur numéro.
Les listes de ressources exclues sont lues en tête, non ligne à ligne. Aucun fichier d'une
autre file n'a été changé.
