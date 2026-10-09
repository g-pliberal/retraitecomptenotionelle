# Étape 9, deuxième partie : les contributions d'équilibre de l'Agirc-Arrco dans ce qui est versé

**La demande.** Le premier point de « Ce qui reste » de la première partie
(note du 7 octobre) : l'ASF avant 2001, l'AGFF de 2001 à 2018, la CEG et la CET
depuis 2019, prélevées pour la retraite complémentaire sans ouvrir de points.
Le compte notionnel ne les porte pas, par la décision du 2 octobre 2026
(action 140, abandonnée : « ce ne sont pas des cotisations ») ; le rendement
du scénario 1 doit, lui, les compter, puisque la paie les supporte. Leur
histoire était à lire aux textes, puis à porter à `cotisations_versees`.

**Ce que disent les textes, lus le jour même.**

- *L'AGFF* (accord du 10 février 2001, PDF de la fédération) : « une
  cotisation sur les salaires versés à compter du 1er avril 2001, supportée par
  les employeurs et les salariés relevant des régimes de retraite
  complémentaire AGIRC-ARRCO », 2,00 % sur la tranche A (1,20 % pour
  l'employeur, 0,80 % pour le salarié) et 2,20 % sur la tranche B, d'un à
  quatre plafonds (1,30 et 0,90 %), recouvrée « dans les mêmes conditions que
  les cotisations » (III.2), et qui « se substitue » à l'ASF (III.1). Le
  recueil des accords de 1993 à 2015 la montre reconduite aux mêmes taux
  (accord du 18 mars 2011, article 2) et étendue « à compter du 1er janvier
  2016 » à la tranche C des cadres, au taux de la tranche B (accord du
  30 octobre 2015, article 3). Ses dépenses, celles de l'ASF qu'elle reprend :
  les points des anciens bénéficiaires des garanties de ressources et la
  retraite complémentaire sans abattement avant soixante-cinq ans.
- *La contribution exceptionnelle et temporaire de l'Agirc* (accord du
  25 avril 1996 relatif au régime des cadres, article 7) : « non génératrice
  de droits », « assise sur la totalité des rémunérations perçues par les
  salariés relevant du régime des cadres », de 0,07 % en 1997 à 0,35 % en 2001,
  partagée comme la cotisation de la tranche B ; reconduite pour 2016 à 2018
  « dans la limite de huit fois le montant du plafond » (accord du 30 octobre
  2015, article 4-1).
- *La CEG et la CET* (accord national interprofessionnel du 17 novembre 2017,
  articles 32, 34, 37 et 38) : 2,15 % sur la tranche 1 et 2,70 % sur la
  tranche 2, jusqu'à huit plafonds, « afin de financer plus particulièrement
  les charges d'anticipation du régime » ; 0,35 % sur les deux tranches « pour
  les participants dont la rémunération excède le plafond » ; 60 % pour
  l'employeur ; « non génératrices de points » (article 34). L'article 2
  « acte le terme » de l'AGFF au 31 décembre 2018 et « met fin » à l'ASF,
  « créée par l'accord du 4 février 1983 ».
- *L'ASF*, elle, ne se lit nulle part. L'assurance chômage la recouvrait, et
  sa convention, agréée au Journal officiel, renvoie à « l'accord du 4 février
  1983 ou [à] tout accord le modifiant ou s'y substituant », sans chiffre ;
  elle ajoute que « cette disposition ne s'applique pas à la collectivité
  territoriale de Saint-Pierre-et-Miquelon » (convention du 1er janvier 1994,
  article 7, § 2, JORFARTI000002363389 ; 33 documents du JORF nomment la
  structure financière avant 2002, aucun n'en écrit le taux). Les taux sont
  ceux de l'IPP : 2 % sous le plafond du 1er janvier 1984, et au-dessus, jusqu'à
  quatre plafonds, du 1er avril 1984 ; 1,80 % sous le plafond au 1er octobre
  1990 ; 1,96 % et 2,18 % au 1er janvier 1994. TRAJECTOiRE porte les mêmes,
  à l'année (`paramCotis.csv`, au commit `0963b57`, lu sans être copié).
- *Deux erreurs d'autrui, relevées en chemin.* Le barème de l'AGFF des cadres
  de l'IPP, et d'OpenFisca qui le transcrit, déplace en 2016 la borne de la
  tranche A à quatre plafonds au lieu d'ajouter la tranche C. La fiche de paie
  du dépôt citait les articles 34 et 35 de l'accord de 2017 pour la CEG et la
  CET, qui sont à l'article 37 : corrigé.

**Ce qui est fait.**

- *La donnée* : `legislation/contributions_equilibre_agirc_arrco.yaml`, cinq
  contributions — l'ASF (`moyenne`), l'AGFF, la CET de l'Agirc, la CEG et la
  CET (`haute`) —, chacune avec les régimes dont l'affiliation la rend due,
  ses barèmes datés en plafonds, pour les cadres et les autres, et les statuts
  que ses textes écartent ; deux entrées au manifeste
  (`agirc_arrco_accords_contributions_equilibre`, `ipp_asf`).
- *Le module* `contributions_equilibre.py` : ce que la paie d'une carrière en a
  supporté, ligne à ligne comme le compte la lit — le revenu d'une année
  travaillée, tronqué l'année du départ, sous un plafond proratisé, pour les
  régimes que le statut rend dus, services passés retirés. Une année qui
  change de barème prélève la moyenne de ses mois. Est cadre, avant 2019,
  l'année affiliée à l'Agirc. Le ministre du culte verse la CEG depuis 2019 sur
  le forfait de sa cotisation, comme la CAVIMAC l'appelle (10,02 % dont
  2,15 %) ; ni Saint-Pierre-et-Miquelon ni la Nouvelle-Calédonie, où la CAFAT
  indemnise le chômage, ne versent l'ASF. Une année de chômage n'en verse
  aucune.
- *Les flux* (`cycle_de_vie.py`) : le scénario 1 verse les contributions toute
  la carrière ; les scénarios 2 à 5, ce que prélève le compte du scénario 4 et,
  jusqu'à la bascule, les contributions, que la paie supportait ; après elle,
  le régime fusionné remplace la complémentaire, et son taux les omet ; le 6
  verse ce que verse le scénario 1 jusqu'à la bascule.
- *Les tests* : `tests/test_contributions_equilibre.py` (rapide, 13 cas : les
  barèmes aux accords, la fiche de paie d'accord avec le dernier barème,
  l'année qui change de barème, le cadre, le seuil de la CET, les statuts
  écartés, le forfait des cultes, le chômage, le départ) ; un cas de plus dans
  `tests/test_cycle_de_vie.py` ; dans `tests/test_cycle_de_vie_references.py`,
  le taux de cotisation de TRAJECTOiRE resserré, le rendement du COR à bornes
  déclarées, et un cas neuf, le rendement de chaque régime de la génération
  2000.
- *Le registre* : le point de TRAJECTOiRE du chantier 138.9 le dit.

**Ce que montrent les confrontations.**

- *TRAJECTOiRE.* Le taux de cotisation du privé du dépôt était de 10 à 12 %
  sous le sien, de 7 à 8 % aux taux moyens de l'Arrco qu'il retient. Il est
  désormais de 3 à 5 % sous lui, et le sien à 0,2-0,4 % près aux taux moyens,
  sur les quinze carrières du privé du témoin : l'écart qui restait était tout
  entier celui des contributions d'équilibre.
- *Le COR compte aussi les contributions.* Son rendement par régime de la
  génération 2000 (figure 3.A) le montre. Au régime général seul, le dépôt est
  sous lui de 0,43 point pour le salarié au salaire moyen, de 0,65 pour le
  cadre ; à l'Agirc-Arrco, avec les contributions, de 0,36 et 0,42 — le même
  écart, qui ne doit donc rien à la complémentaire ; sans elles, il serait
  au-dessus de lui de 0,39 et 0,17 point. L'annexe méthodologique de 2026
  (§ 2.3, c) dit seulement « seules les cotisations sont retenues ».
- *Le rendement du cas type n° 2 en perd 0,22 à 0,25 point* : 1,29 % contre
  1,24 pour la génération 1955, 1,04 contre 1,21 pour 1960, 0,87 contre 1,17
  pour 1963, 0,77 contre 1,11 pour 1964, 0,41 contre 0,88 pour 1970. Le dépôt
  décroît deux fois et demie plus vite que le COR d'une génération à l'autre ;
  l'oubli des contributions compensait l'écart des générations récentes, que
  le test déclare désormais avec ses bornes. Sa cause, commune aux deux
  régimes, reste à trouver.
- *Le cadre et le non-cadre de la génération 2000* s'écartent de 0,97 point,
  contre 0,78 au COR et 0,86 avant ; les cas types de la grille ne sont pas
  ceux du COR.

**Ce que dit la grille, à code égal** (avant → après ; `python
scripts/cycle_de_vie.py`). Rendement interne réel du salarié au salaire
moyen : au scénario 1, 3,45 → 3,29 % pour la génération 1940, 1,51 → 1,26 %
pour 1970, 1,55 → 1,31 % pour 2000 ; au scénario 4, 1,41 → 1,24 %, 0,71 →
0,51 % et 0,29 → 0,26 %, la génération 2000 cotisant presque toute sa carrière
après la bascule. Le cadre perd 0,27 à 0,34 point au scénario 1. L'écart du
scénario 1 au scénario 4 de la génération 2000 passe de 1,26 à 1,05 point au
salaire moyen, de 0,66 à 0,34 pour le cadre. La valeur actuelle nette du
salarié au salaire moyen né en 2000 passe de 0,20 à −0,80 année de dernier
revenu au scénario 1. Le contractuel public, à l'Ircantec, ne bouge pas ; le
patrimoine, qui ne compte que les pensions, non plus.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les prélèvements sur les pensions depuis 1980*, que l'IPP publie
   (registre, chantier 138.9) : le rendement net du COR en dépend, celui des
   générations parties avant 2018 surtout.
2. *L'écart au COR des générations 1963 à 1970*, commun au régime général et
   à l'Agirc-Arrco : les projections du dépôt d'abord — le salaire moyen, la
   valeur de service —, puis les carrières.
3. *Les indicateurs à chaque âge de départ*, l'âge d'équilibre, le portage et
   l'affichage, la génération 1941 : les points 3 à 6 de la note du 7 octobre.
4. *Les contributions, à leurs bords* : l'accord du 4 février 1983 et ceux qui
   l'ont modifié, que personne ne publie, pour l'ASF ; les « conditions
   particulières » de l'accord de 2017 à Saint-Pierre-et-Miquelon et en
   Nouvelle-Calédonie (article 8) ; le ministre du culte avant 2019.
