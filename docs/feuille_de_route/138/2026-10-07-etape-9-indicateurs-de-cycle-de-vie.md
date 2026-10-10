# Étape 9, première partie : les indicateurs de cycle de vie, confrontés au COR, à TRAJECTOiRE et à l'OCDE

**Reprise, au 10 octobre 2026.** Fait : `cycle_de_vie.py`, onze indicateurs
des six systèmes, sous la convention de l'OCDE et sous celle du COR, les
contributions d'équilibre, chaque âge de départ, les prélèvements de chaque
année ; le 10 octobre, l'écart au COR des générations 1963 à 1970, trouvé :
le dépôt retrouve la série brute du COR de 2025, et celle de 2026 en est une
révision que le COR ne dit pas, déclarée. Reste, dans cet ordre : l'âge
d'équilibre ; le portage et l'affichage, avec l'étape 10 ; la génération
1941. Commencer par l'âge d'équilibre. Détail : « Ce qui reste » de la note
`2026-10-10-etape-9-ecart-au-cor.md`.

**La demande.** L'étape 9 de l'action : « les indicateurs de cycle de vie, par
cas type et génération, sous les six systèmes : rendement interne, durée de
retraite, taux de récupération, patrimoine retraite ; confrontés à l'OCDE de
2025 et aux cas types du COR ». Treize points du registre y renvoyaient
(chantier « 138.9 »), chez Destinie 2, TRAJECTOiRE, le COR, PRISME, le
simulateur de pilotage, le modèle norvégien, l'IJM, l'ETK, PROST et l'OCDE.

**Ce que disent les références, lues le jour même.**

- *Le COR* (rapport annuel de juin 2026, p. 138-141 ; annexe méthodologique en
  ligne, § 2.3 ; document n° 6 de la séance du 21 avril 2022). La durée de
  retraite d'une génération est « 60 + espérance de vie à 60 ans », moins son
  âge moyen de départ. Le rendement interne est « le taux d'actualisation qui
  assure une stricte égalité entre la somme des pensions perçues et des
  cotisations payées », calculé sur le cas type n° 2 (non-cadre du privé à
  carrière continue), cotisations seules, droits propres hors droits
  familiaux, décès à 60 + e60 de la génération, les deux sexes réunis ; net
  depuis 2026, au taux plein de CSG ; flux actualisés selon le SMPT dans le
  rapport (0,83 % pour la génération 2000), selon les prix dans l'annexe
  (1,5 %). Pour le public, le COR ne compte que la retenue de l'agent : la
  contribution de l'État « ne reflète que le montant de la contribution qui
  permet de garantir en dernier ressort l'équilibre du régime » (document n° 9
  du 17 novembre 2022).
- *TRAJECTOiRE* (commit `0963b57`, lu sans être copié : EUPL).
  `txRecuperation` est la somme des pensions sur celle des cotisations,
  salariales et patronales, base et complémentaires, chaque montant divisé par
  le SMPT de son année ; `txAnnuite`, la même somme sur celle des
  rémunérations ; la durée de carrière, le nombre d'années à rémunération
  positive ; le décès, à `round(60 + e60)` de la table du COR plus six mois.
  Il ne compte aucune contribution d'employeur pour l'État ni pour la plupart
  des régimes spéciaux, compte à l'Arrco le taux contractuel moyen des
  entreprises, et l'AGFF puis la CEG.
- *L'OCDE* (*Pensions at a Glance 2025*, API SDMX `DSD_PAG@DF_PAG` ; le site
  refuse les robots). Le patrimoine retraite est la valeur, au départ, des
  pensions des régimes obligatoires, actualisées à 1,5 % réel sur la mortalité
  de cohorte de l'ONU, en années de salaire individuel ; la carrière, une
  entrée à 22 ans en 2024 au même multiple du salaire moyen (44 968 €), un
  départ à 65 ans ; les prix à +2 %, les salaires réels à +1,25 % — 3,275 %
  nominal, le produit.

**Ce qui est fait.**

- *Le module* `src/retraite_notionnelle/cycle_de_vie.py`. Chaque carrière, sous
  chaque système, devient deux chroniques en euros courants. CE QUI EST VERSÉ :
  au scénario 1, les cotisations salariales et patronales du droit en vigueur,
  et de l'État la part que la Cour des comptes rattache à la retraite de
  l'agent (`ContributionEtat.RETRAITE_SEULE`, le compte du scénario 4 bâti sans
  la fusion de la bascule) ; aux scénarios 2 à 5, ce que prélève le compte du
  scénario 4 — les mêmes jusqu'à la bascule, le taux du régime fusionné
  ensuite ; au 6, son taux unique et les deux parts de son pilier. CE QUI EST
  REÇU : le scénario 1 mené par ses textes jusqu'à l'année courante
  (`faire_vivre`), puis par la convention de la page Coût (les prix, la valeur
  de service convenue de l'Agirc-Arrco) ; les systèmes notionnels par la règle
  de leur compte et du stock à la bascule, sur toute la retraite — la
  `RevalorisationServie` du simulateur s'arrêtait à l'année courante ; ni
  ASPA, ni garantie vieillesse, ni réversion. Deux conventions : la survie de
  génération (l'OCDE, le défaut), intégrée exactement sous la force de
  mortalité constante par cellule de `survie_annuelle` ; un âge de décès fixe
  (`convention_cor` : 60 + e60, les deux sexes, net au taux plein). Onze
  indicateurs : durée de retraite, part de vie, durée relative à la carrière,
  taux de récupération, d'annuité, de remplacement sur le cycle de vie,
  rendement interne réel et relatif au SMPT, patrimoine, valeur actuelle nette
  et taux de remplacement au décès (ces deux derniers, de PROST). La grille
  entière se calcule en 1,3 s, après les 5,5 s de la grille des cas types.
- *Le jeu `ocde_2025`* : une section `jeux_de_reference` de
  `macro/hypotheses_projection.yaml`, que `DonneesMacro` et son jumeau
  JavaScript nomment comme un scénario, sans en faire une variante du COR —
  aucun compte publié ne lui répond, et le test des variantes l'exige. Le
  paquet du site la porte.
- *Deux témoins* : `scripts/fetch/cor_cycle_de_vie.py` lit les figures 3.6,
  3.7 et 3.A du classeur de la partie 3 ; `scripts/fetch/ocde_pensions.py`,
  l'API de l'OCDE. Tous deux au registre des sources.
- *Les tests* : `tests/test_cycle_de_vie.py` (rapide, 21 cas : un rendement
  connu d'avance se retrouve, une valeur nette s'annule à son rendement…) et
  `tests/test_cycle_de_vie_references.py` (contrôle, 10 cas) ;
  `scripts/cycle_de_vie.py` imprime la grille, `--cor` sous les conventions du
  COR.
- *Le registre* : dix points repris, trois restent à reprendre (les
  prélèvements de l'IPP, la pension par étage du modèle norvégien, l'âge de
  l'ETK) et un naît de celui de TRAJECTOiRE (ses indicateurs à chaque âge de
  départ, nets).

**Ce que montrent les confrontations.**

- *Les tables de mortalité sont celles de l'INSEE.* L'espérance de vie à 60 ans
  des générations 1960 à 2000 est celle du COR à 0,07 an près, par sexe ; de
  1940 à 1959, à 0,45 an près. Sauf la génération 1941 : +0,62 an pour les
  hommes, +0,65 pour les femmes. Ses quotients observés sont de 5 à 10 % sous
  ceux de 1940 et de 1942 à chaque âge de 60 à 83 ans ; la table de l'INSEE
  ne montre pas cette marche, et le diviseur de cette génération en hérite. À
  porter à la session des données.
- *Le rendement interne net du cas type n° 2* (figure 3.7), sous les
  conventions du COR et sur les carrières que TRAJECTOiRE a bâties pour lui :
  1,52 % contre 1,24 % pour 1955, 1,29 contre 1,21 pour 1960, 1,12 contre 1,17
  pour 1963, 1,03 contre 1,11 pour 1964, 0,66 contre 0,88 pour 1970 — à 0,3
  point près, décroissant des deux côtés. Le dépôt prélève toute la retraite
  aux taux de 2026 (le rendement des premières générations en est abaissé) et
  ne porte pas l'AGFF ni la CEG (il en est relevé). Génération 2000 (figure
  3.A) : le cadre rend 0,87 point de moins que le salarié au salaire moyen,
  0,79 au COR.
- *TRAJECTOiRE* : la durée de retraite rapportée à la carrière, exactement,
  sur ses cas types du COR, avec un âge de décès par génération (86,5 ans pour
  1955, 87,5 pour 1960 à 1964, 88,5 pour 1970) ; quatre cas comptent d'autres
  années (chômage du cas 3 de 1955, AVPF du cas 4). Le taux d'annuité, la
  pension de départ recalée sur la sienne : 0,90 à 1,03 fois le sien. Le taux
  de cotisation du privé : 10 à 12 % sous le sien ; aux taux moyens de l'Arrco
  qu'il retient, l'écart se réduit de 2,6 à 5 points, et le reste, 7 à 8 %,
  est celui des contributions d'équilibre. Pour l'État, le dépôt verse trois à
  six fois plus que lui, qui ne compte que la retenue ; réduit à elle, il est
  le sien à la RAFP près.
- *L'OCDE* : le salarié entré à 22 ans en 2024 part à 65 ans au taux plein,
  comme elle l'écrit. Taux de remplacement brut : 57,6 % à la moitié du
  salaire moyen (56,6 à l'OCDE), 53,9 au salaire moyen (56,6), 42,5 au double
  (47,4). Le régime général y sert 42,7 % au salaire moyen — la moitié d'un
  salaire annuel moyen revalorisé sur les prix quand les salaires réels
  montent de 1,25 % — ; l'écart est celui de l'Agirc-Arrco, le même quart de
  la pension complémentaire du dépôt aux deux niveaux : sa valeur de service
  suit la convention du COR, sous la valeur d'achat. Patrimoine : la valeur
  d'un euro de rente est celle de l'OCDE à 1,2 % près pour un homme, 5,6 %
  sous elle pour une femme, que la mortalité de l'ONU fait vivre plus
  longtemps que celle de l'INSEE ; 11,1 années de salaire contre 11,5 pour un
  homme, 11,8 contre 13,1 pour une femme.

**Le même soir, après l'étape 7.** Les quotients projetés de l'INSEE, que
l'étape 7 a substitués à la loi de Gompertz-Makeham et publiés juste après
celle-ci, rapprochent encore les tables du dépôt de celles du COR :
l'espérance de vie à 60 ans des générations 1960 à 2000 concorde à 0,02 an
près, celle des générations 1940 à 1959 à 0,08 an, et l'écart de la
génération 1941 tombe à +0,32 an pour les hommes et +0,22 pour les femmes —
la marche de ses quotients observés demeure. Le rendement du cas type n° 2
ne bouge que d'un centième ; la rente de l'OCDE vaut 1,9 % de plus que la
sienne pour un homme, 5,1 % de moins pour une femme. Les tolérances du test
de l'espérance de vie sont resserrées, la bande des hommes de l'OCDE portée à
3 %.

**Ce que dit la grille** (conventions du dépôt ; `python scripts/cycle_de_vie.py`).
Le rendement interne réel du système actuel décroît de génération en
génération : 3,5 % pour le salarié au salaire moyen né en 1940, 1,5 % pour
celui de 2000 ; 2,9 puis 0,8 % pour le cadre ; 10,1 puis 1,5 % pour le
militaire radié après vingt-cinq ans. Le compte notionnel, part patronale
comprise (scénario 4), rend 1,4 puis 0,3 % au salarié au salaire moyen, la
proposition (scénario 6) 1,4 puis 0,2 % ; le scénario 2, qui ne porte au
compte que la part salariale de ce qui est versé, −1,9 puis −2,3 %. Le
patrimoine retraite du salarié au salaire moyen né en 2000 vaut 12,0 années
de son dernier revenu au scénario 1, 7,7 au 4 et 8,3 au 6 ; sa pension finit
la retraite à 47,8 % du salaire d'alors.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les contributions d'équilibre de l'Agirc-Arrco dans ce qui est versé* :
   l'ASF avant 2001, l'AGFF de 2001 à 2018, la CEG et la CET depuis 2019. Le
   compte notionnel ne les porte pas, par un choix déclaré
   (`docs/limites/5-hors-du-modele.md`) ; le rendement du scénario 1 doit, lui,
   les compter : elles sont prélevées pour la retraite. Leur histoire est à
   lire aux textes (accords de 1983, 2001, 2017), puis à porter à
   `cotisations_versees` ; la confrontation à TRAJECTOiRE le dira.
2. *Les prélèvements sur les pensions depuis 1980*, que l'IPP publie (registre,
   chantier 138.9) : le rendement net du COR en dépend, celui des générations
   parties avant 2018 surtout.
3. *Les indicateurs à chaque âge de départ*, de l'âge d'ouverture à
   l'annulation de la décote, comme TRAJECTOiRE et le document n° 6 du COR de
   2022, et sous les quatre productivités ; la pension nette rapportée à
   l'ASPA.
4. *L'âge d'équilibre* : celui où le diviseur d'une génération égale celui de
   la génération de référence à 65 ans (ETK), et celui qui tient constante la
   part de la vie en retraite (le simulateur de pilotage).
5. *Le portage et l'affichage* : un jumeau JavaScript de `cycle_de_vie.py`, et
   la page des carrières types, avec l'étape 10 ; l'affirmation du site sur le
   rendement interne passerait alors de `hors_modele` au contrôle.
6. *La génération 1941*, aux données : une marche de ses quotients observés.
   Les limites de l'étape s'écrivent à sa fin.
