# Étape 12, première partie : la fiche de paie d'un agent public — la RAFP, l'indemnité compensatrice de la CSG, le taux d'équilibre sur le traitement

**Reprise, au 10 octobre 2026.** Fait : le coût du travail complet d'un agent
public — la RAFP sur ses primes, l'indemnité compensatrice de la hausse de la
CSG, le taux d'équilibre de l'État sur le seul traitement —, dans les deux
moteurs. Reste, une session par point : le micro-entrepreneur par son chiffre
d'affaires et le chemin de la Cipav (rang moyen du classement) ; la veille du
projet de loi de financement pour 2027, à son vote ; puis, au rang léger, le coût
du travail complet du privé (la taxe sur les salaires, le forfait social, les
taxes hors protection sociale), la seconde pension revalorisée et replafonnée,
les artistes-auteurs sous le seuil, la dispense des cotisations minimales, le
rachat de trimestres, le dirigeant assimilé salarié. Détail : « Ce qui reste ».

**Le 10 octobre 2026, la demande.** Le propriétaire : porter sur la fiche de
paie, en Python puis en JavaScript, la cotisation de la RAFP sur les primes,
parts salariale et employeur, dans la limite que fixe la fiche du régime, et
l'indemnité compensatrice de la hausse de la CSG des agents publics, versée
depuis 2018, qui relève leur brut, avec ce que la proposition en fait ; mesurer
ce que cela change à la page de la RAFP et au gain net de la fonctionnaire de
l'exemple du README (+33,1 %), régénérer, récrire la limite 5 ter ; revérifier
la confrontation à TRAJECTOiRE du revenu net des indicateurs de cycle de vie,
qui en hérite.

**Ce que dit le droit, lu le jour même** (journal de veille du 10 octobre ;
`legislation/indemnite_compensatrice_csg.yaml`, qui cite chaque texte).

- *La RAFP* : 5 % pour l'agent, 5 % pour l'employeur, sur les primes dans la
  limite de 20 % du traitement indiciaire brut (décret n° 2004-569, article 2),
  que la fiche du régime portait déjà et que le compte et le scénario 1 lisent
  par `PeriodeRegime.part_du_revenu`.
- *L'indemnité* (loi de finances pour 2018, article 113 ; décret n° 2017-1889,
  articles 2 et 5 ; circulaire du 15 janvier 2018) : pour l'agent payé au
  31 décembre 2017, 1,6702 % de sa rémunération brute de 2017, moins la
  contribution exceptionnelle de solidarité, la maladie et le chômage dus sur
  elle, par 1,1053 ; pour l'agent nommé ou réintégré depuis, 0,76 % de sa
  première rémunération mensuelle, sauf le contractuel couvert par le régime
  général. Réévaluée au 1er janvier 2019 (décret d'origine) et 2020 (décret
  n° 2019-1595) si la rémunération a progressé, chaque 1er janvier depuis 2021
  si elle « a évolué » (décret n° 2020-1626), quotité et maladie neutralisées.
  Soumise à la RAFP, à la CSG et à la CRDS, pas à la retenue pour pension. Les
  décrets de 2019 et de 2020 ne sont pas dans l'index de la DILA, qui ne porte
  que le champ social : lus au Journal officiel, en PDF.
- *La CES de 2017*, que l'indemnité déduit : 1 % de la rémunération nette des
  cotisations, dans la limite de quatre plafonds (L. 5423-27, L. 5423-32),
  rien sous le traitement de l'indice majoré 313 (R. 5423-52 depuis le 1er mars
  2017).
- *Le taux d'équilibre de l'État* : 82,28 % du traitement en 2026, « fraction de
  l'assiette de la retenue pour pension (traitement indiciaire brut et NBI ; les
  primes en sont exclues) », dit sa série elle-même.

**Ce qui est décidé, et pourquoi.**

- *La proposition garde la RAFP.* Le README la sert à l'identique dans les six
  scénarios, cotisée jusqu'au départ (« une réforme de la répartition ne les
  atteint pas ») : la fiche de la proposition la prélève donc aussi, au même
  taux de la rémunération entière — sauf quand le compte convertit la RAFP
  (`isoler_capitalisation` à faux), où le taux unique la remplace.
- *La proposition garde l'indemnité.* Ni le README ni le programme ne la
  nomment ; elle ne finance aucune retraite. Elle reste versée, et le taux
  unique de la proposition, assis sur toute la rémunération, la prélève.
- *La ligne de carrière ne la porte pas.* Le revenu d'un agent public est son
  traitement et ses primes, l'assiette de ses pensions ; la fiche ajoute
  l'indemnité, tirée du décret et de la carrière, et la compte avec les primes,
  hors de la retenue, dans la RAFP. La saisie d'un net la prête à un agent payé
  fin 2017 dont la rémunération a suivi le salaire moyen ; un brut saisi se lit
  sans elle.
- *Seuls les agents publics à retenue la touchent* : la famille `public` au
  profil `agent_seul`. Le contractuel en est écarté : en poste fin 2017, la
  maladie et la CES qu'il payait en absorbaient presque tout, 0,03 % de sa
  rémunération ; recruté depuis, le décret l'exclut. Le marin, l'artiste de
  l'Opéra, l'agent du port de Strasbourg ne sont pas des agents publics.
- *Trouvé en chemin, et corrigé* : la correction du 9 octobre avait ôté les
  primes de la retenue, non de la dépense que la proposition libère, qui
  comptait 82,28 % des primes aussi. Le taux d'équilibre et ce qu'il paie de
  départs anticipés portent désormais sur le seul traitement
  (`BlocRetraite.part_traitement`).

**Ce qui est fait.**

- *Les données* : `legislation/indemnite_compensatrice_csg.yaml`, ses textes et
  ses paramètres ; au paquet, `indemnite_compensatrice_csg`. Dans
  `prelevements_remuneration.yaml`, la RAFP et l'indemnité nommées, et la fin de
  la CES rendue à l'article 112 de la loi de finances pour 2018 — le fichier
  l'attribuait à l'article 143 de la loi n° 2016-1918, qui supprime le Fonds de
  solidarité.
- *Le modèle, dans les deux moteurs* : `donnees/indemnite_csg.py` et
  `moteur/js/indemnite_csg.js` (le montant, ses réévaluations, la CES) ; dans
  `remuneration.py` et `remuneration.js`, l'étage de la RAFP du droit en
  vigueur (`_etage_hors_repartition`), gardé par la proposition (`conservees`),
  l'indemnité de la carrière (`indemnites_de_la_carriere`) ajoutée au brut et
  comptée avec les primes (`part_primes_de_la_fiche`), l'indemnité prêtée à la
  saisie (`indemnite_stylisee`), le taux d'équilibre sur le traitement ; dans
  `cycle_de_vie.py`, le revenu net de chaque année, RAFP et indemnité comprises
  (`indemnites_des_lignes`). Une sonde, `indemnite_csg`.
- *Le site* : le paragraphe « Ce que la fiche ne porte pas » d'un agent public,
  qui disait la RAFP exclue par construction.
- *Les tests* : `test_indemnite_csg.py`, dix cas — l'exemple du réexamen de 2019
  de la circulaire, au centime (17 € portés à 18,23 €), les trois coefficients
  tirés des taux de la CSG, la CES, les recrutés, l'année sans paie, les
  bénéficiaires, les assiettes de l'indemnité, la fonctionnaire de l'exemple, la
  RAFP remplacée sans isolement, le taux d'équilibre sur le traitement ; cinq
  tests repris, qui supposaient la fiche sans RAFP ni indemnité.

**Les mesures.**

- *La fonctionnaire de l'exemple du README* (née en 1975, un cinquième de
  primes) : son indemnité vaut 31,90 € par mois en 2026, sa RAFP 31,15 € ; son
  traitement net passe de 3 177,20 € à 3 174,90 €. Ce que la proposition lui
  rend passe de +1 052,91 € à +808,83 € par mois, de +33,1 % à +25,5 % : la RAFP
  seule −0,1 point, l'indemnité seule −0,1, l'assiette du taux d'équilibre
  −7,2. Le militaire passe de +38,3 % à +29,6 %. Son traitement monte, sous la
  proposition, d'un quart sans primes (+27,1 %), d'un cinquième à un cinquième
  de primes (+20,2 %), d'un sixième à trois dixièmes de primes (+16,8 %).
- *La page de la RAFP* (`simuler_rafp`) : le traitement brut de 3 894,12 € à
  3 926,01 € ; la retraite à la charge de l'agent de 345,80 € à 376,95 € sous le
  droit en vigueur, de 314,14 € à 336,06 € sous la proposition ; le gain de
  1 053 € à 809 € par mois, son cumul jusqu'au départ de 188 800 € à 145 004 € ;
  l'épargne volontaire de 248,14 € à 235,88 € par mois. Trois autres pages
  bougent : la même fonctionnaire au taux de l'État entier, comme elle, et deux
  fonctionnaires sans primes, dont le gain perd 4 et 5 € par mois. Aucun des
  799 témoins de simulation ne bouge.
- *Le revenu net du cycle de vie* de la même fonctionnaire : le rapport du net
  au brut perd 0,8 point par la RAFP depuis 2005 (0,830 → 0,822 en 2017) et en
  regagne 0,7 par l'indemnité depuis 2018 (0,816 → 0,815 en 2026).
- *La saisie d'un net* : le brut d'un agent public, de −1 % à +0,1 % selon ses
  primes et son niveau — l'indemnité de qui était sous le seuil de la CES en
  2017 est presque double —, et sa pension le suit.
- *TRAJECTOiRE*, qui prélève la RAFP sur le net et ne porte pas l'indemnité : la
  RAFP rapproche les fonctionnaires de près d'un point, l'indemnité les en
  éloigne d'autant pour les départs depuis 2019. Les 65 cas concordants restent
  à 0,8 % près ; le policier (cas 8), de 1,013 à 1,029 fois, reste dans ses
  bornes ; l'aide-soignante (cas 9), de 0,934 à 0,994 fois, en sort, et ses
  bornes déclarées passent de [0,94 ; 0,99] à [0,93 ; 1,0], la cause récrite.

**Ce qui reste.**

1. *La pension de la RAFP* ne compte pas l'indemnité, que la fiche prélève : un
   douzième de ses points à qui touche un dixième de primes, rien au-delà du
   plafond. Au scénario 1, avec `part_du_revenu`, à la session des données.
2. *La GIPA et les jours de compte épargne-temps*, que la RAFP prend sans
   plafond (fiches `rafp_gipa_hors_plafond`, `rafp_compte_epargne_temps`).
3. *Le sens de la réévaluation depuis 2021* : « a évolué » ; aucune source lue ne
   l'applique à une baisse. La quotité et les congés de maladie de l'article 4.
4. *Le site*, pour la session des pages : la fiche d'un agent public nomme
   « traitement indiciaire brut » sa rémunération entière ; sa lecture dit
   encore « le traitement indiciaire brut ne bouge pas » et son incidence « est
   tenu fixe », que le partage du 20 septembre a rendus faux ; une ligne de
   l'indemnité au tableau.
5. *Le reste de l'étape* : voir le bloc « Reprise ».
