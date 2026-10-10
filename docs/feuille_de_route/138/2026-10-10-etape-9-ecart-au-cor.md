# Étape 9, cinquième partie : l'écart au COR du rendement des générations 1963 à 1970

**La demande.** Le propriétaire, le 10 octobre 2026 : trouver pourquoi le
rendement interne net du cas type n° 2, sous les conventions du COR et sur les
carrières que TRAJECTOiRE a bâties pour lui, décroît deux fois et demie plus
vite que celui du COR (1,30 % contre 1,24 pour 1955, 0,87 contre 1,17 pour
1963, 0,41 contre 0,88 pour 1970) ; le corriger si c'est un défaut du dépôt, le
déclarer précisément si c'est une convention. Trois pistes, dans l'ordre : les
projections, les carrières, les cotisations.

**Ce que disent les références, lues le jour même.**

- *Le COR de juin 2026*, ses classeurs (parties 1, 2, 3 et annexe). La
  productivité horaire de son scénario de référence : 0,86 % en 2026, 0,78 à
  0,79 % de 2029 à 2032, 0,70 % dès 2040 (figure 1.10) ; la rémunération nette moyenne
  réelle : −0,20 % en 2026, +0,48 à +0,60 % de 2027 à 2029, +0,79 à +0,70 %
  ensuite (figure 2.4). Le profil du cas type n° 2, en part de la rémunération
  moyenne par tête de l'année, et son âge d'entrée par génération (figures A2.4,
  A2.2). Son taux de cotisation, année par année et par génération (figure
  3.1) : 27,89 % en 2024 et 2025, Cnav, Agirc-Arrco et CEG réunies, ceux du
  dépôt depuis 2006 ; 23,6 % en moyenne sur la carrière de la génération 1955,
  27,2 % pour 1970. Ses taux de remplacement par régime (figure 3.3), d'où
  l'on tire une pension de la Cnav du cas type de la génération 2000
  d'environ 0,32 salaire moyen à la liquidation, celle du dépôt. Le rendement selon l'espérance de vie
  et la productivité (figures 3.32 et 3.36). Une phrase, note 140 : « Dans les
  précédents rapports annuels du COR, le TRI était évalué à partir des
  rémunérations brutes. » Et l'encadré du rendement selon le revenu et le
  genre : « les dispositifs d'allègement de cotisations sur les bas salaires
  bénéficient davantage aux femmes » ; le SMIC y est « avec exonérations »
  (2,9 %) et « hors exonérations » (0,3 %).
- *Son annexe méthodologique*, § 2.3 c, comme en 2025 : « Seules les
  cotisations sont retenues – sans les allègements (qui tendraient à augmenter
  le TRI) » ; et la note de méthode du 17 mai 2017 (document n° 10) : « les
  cotisations sont considérées sans allègements ». Le document n° 6 du
  21 avril 2022 : le cas type de 1960 « n'a pas bénéficié d'exonérations
  générales » — sur l'ancien profil, d'avant 2023.
- *Le COR de juin 2025*, partie 3, figure 3.7 : le rendement BRUT du même cas
  type, génération par génération — 1,69 % pour 1955, 1,30 pour 1963, 0,75
  pour 1970, 0,50 pour 2000 —, sous la mortalité des projections de l'Insee de
  2021 (espérance de vie à 60 ans de la génération 2000 : 31,29 ans, contre
  30,58 en 2026).
- *TRAJECTOiRE* (commit `0963b57`, lu sans être copié : EUPL), dont le COR tire
  ses cas types (« Source : Drees, modèle Trajectoire »). Son script des cas
  types bâtit le salaire comme le profil du COR fois le salaire moyen de la
  Cnav (`parametres$smpt[caisse == "Cnav"]`, « il faudrait le smpt tous
  régimes, mais celui de la cnav s'en rapproche »), lu dans ses hypothèses du
  COR de 2024 : 1,055 fois la rémunération moyenne par tête du COR — revenu
  mixte et salaires sur l'emploi total —, à 1 % près, de 1974 à 2033. Les
  carrières du témoin en sont, à l'euro. Son rendement interne
  (`indicAgreg`) actualise par ce même salaire moyen. Il n'a aucun allègement.

**Ce que montrent les mesures** (dépôt moins COR de 2026, en points ; avant :
+0,06, −0,17, −0,30, −0,34, −0,48 pour 1955, 1960, 1963, 1964, 1970).

- *Les projections.* La rémunération moyenne réelle du COR (figure 2.4) au lieu
  de 0,7 % dès 2026 : +0,02 à +0,03. Ses conventions de l'Agirc-Arrco, taux
  moyen des entreprises et valeur de service (`Parametres.conventions_cor`) :
  −0,02 à −0,05. Ce n'est pas la cause.
- *Les carrières.* Refaites sur le profil du COR et le salaire moyen du dépôt,
  aux mêmes dates : −0,03 à +0,04. Actualisées selon la rémunération moyenne
  par tête du COR au lieu du salaire moyen des salariés du dépôt (qui a crû de
  0,26 point par an de plus qu'elle de 2004 à 2024) : +0,06 à +0,11, pour
  toutes les générations, la pente intacte. Aucun âge de départ ne rejoint le
  COR, et le pilote du dépôt retrouve ceux de TRAJECTOiRE à un trimestre
  près. Le taux de récupération du dépôt est celui de TRAJECTOiRE à 3,5 %
  près : ses flux décroissent aussi vite.
- *Les cotisations.* Les mêmes taux que le COR, contributions d'équilibre
  comprises ; et, selon son annexe, sans les allègements, comme le dépôt.
- *La cause.* Le rendement BRUT du dépôt, conventions du COR pour le reste,
  retrouve la série de juin 2025 : −0,08, −0,17, −0,13, −0,03, −0,03, la pente
  de 1955 à 1970 à 0,04 près ; −0,07 à +0,05 sur la rémunération moyenne du
  COR. Sur toute la courbe, le profil du COR de 1940 à 2000 au premier âge du
  taux plein : à 0,17 près, +0,13 pour 2000. Le net retire 0,30 point au
  dépôt, à chaque génération. La série de 2026 n'est pas celle de 2025 moins
  autant : le COR l'a révisée d'autre chose, −0,14 pour 1955, rien pour 1960,
  +0,17 pour 1963, +0,31 pour 1964, +0,44 pour 1970, +0,6 pour 2000. L'écart
  de 2026 est cette révision, au reste de 2025 près. Elle ne tient ni à la
  mortalité (celle de 2026 l'abaisserait), ni à la productivité (0,7 % les
  deux années), ni aux taux. Seul candidat trouvé, les allègements : la
  réduction dégressive de 2026, imputée à la retraite par la clé de la loi et
  retranchée dès 2019, rendrait +0,10, +0,13 et +0,28 point aux générations
  1963, 1964 et 1970, +1,06 à celle de 2000 — l'allure de la révision, non sa
  mesure.

**Ce qui est fait.**

- *Le témoin du COR* (`scripts/fetch/cor_cycle_de_vie.py`,
  `tests/temoins/cor_cycle_de_vie.json`) lit aussi la figure 3.7 du rapport de
  juin 2025 : `rendement_cas_type_2_brut_2025`, avec sa source.
- *Les tests* : `test_le_rendement_brut_du_cas_type_2_est_celui_du_cor_de_2025`
  (la série brute de 2025 à 0,2 point, la pente à 0,1, le net à 0,30 point du
  brut, la révision de 2026 dans ses bornes, `REVISION_DE_2026`) ;
  `ECARTS_RENDEMENT` garde ses bornes, sa cause dite.
- *Une docstring fausse* de `cycle_de_vie.py` : la valeur de service que le
  COR projette ne mène l'Agirc-Arrco que sous le simulateur de la page Coût ;
  l'individuel, que les confrontations emploient, la mène sur les prix.
- *Le registre* (chantier 138.9) et la source du témoin le disent.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'âge d'équilibre* : l'ETK, le simulateur de pilotage.
2. *Le portage et l'affichage*, avec l'étape 10 : les jumeaux JavaScript de
   `cycle_de_vie.py`, de `prelevements_historiques.py` et de
   `contributions_equilibre.py`.
3. *La génération 1941*, aux données.
4. *La révision de 2026*, au COR : la demander à son secrétariat général, ou
   la lire dans le document de séance qui l'a préparée, quand il paraîtra. Si
   ce sont les allègements, leur histoire (exonération de 1993, ristourne de
   1995, Aubry, Fillon, réduction de 2026) et leur clé d'imputation, à porter
   à `cotisations_versees` comme une variante de la convention du COR.
5. *La rémunération moyenne par tête du COR* (revenu mixte et salaires sur
   l'emploi total, comptes nationaux), à la session des données : elle
   actualiserait le rendement comme lui, +0,06 à +0,11 point.
