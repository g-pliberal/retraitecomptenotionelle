# Étape 8, troisième partie : le SMIC net agricole refait des taux salariaux, et ce que la MSA publie en euros

**Le 14 octobre 2026, la demande.** Les deux premiers restes de l'étape :
« un exemple chiffré de la MSA, lu à sa source et rejoué par les deux
moteurs ; puis le SMIC net agricole de 2015 à 2020 et de 2022, certifié »
(session de nuit, tâche 12).

**Ce que dit le droit** (journal de veille du 14 octobre). L. 732-63 porte la
pension d'un chef à un pourcentage de 1 820 fois le SMIC « après déduction des
contributions et cotisations obligatoires dues au titre des régimes de base et
complémentaire légalement obligatoire des salariés agricoles » du 1er janvier.
Aucun texte n'en fixe le montant ; la MSA le calcule.

**Ce qui est fait.**

- *La déduction, expliquée.* C'est la somme des taux salariaux d'un non cadre
  d'une entreprise de la production agricole au SMIC : vieillesse, maladie et
  chômage tant qu'ils ont existé, CSG et CRDS sur 98,25 %, AGRICA (3,875 %
  jusqu'en 2018 avec l'AGFF, 3,93 % et la CEG depuis 2019) et l'AFNCA,
  0,01 % : 22,845 % en 2015, 22,945 en 2016, 22,995 en 2017, 22,46525 en
  2018, 21,63025 depuis 2019. Les 0,79 point qui restaient inexpliqués sont la
  part salariale d'AGRICA au-delà de celle du régime général (3,93 au lieu de
  3,15) et l'AFNCA. Taux lus dans le barème des cotisations sur salaires au
  1er janvier 2016 (ministère de l'agriculture) et dans le barème de la MSA au
  1er avril 2020.
- *Le récupérateur* `scripts/fetch/msa_smic_net_agricole.py` refait chaque
  année du SMIC brut et de ces taux, et confronte le calcul à sept montants
  publiés : 1 161 € et 871 € en 2018 (Sénat, rapport n° 315), 1 206,44 € et
  904,83 € en 2020 (Assemblée nationale, rapport n° 3071), 1 035,57 € en 2021,
  1 067,91 € au 1er janvier 2022 et 1 214,40 € en 2026 (MSA). Il les redonne
  tous au centime (à l'euro pour les montants ronds) ; `--verifier` relit
  chacun à sa source, ce qu'il fait ce jour sans écart.
- *Le fichier* `complement_differentiel_rco.csv` : 2015 à 2018 refaits du
  calcul (7,4146, 7,4512, 7,5157, 7,6604 € de l'heure, quelques dix-millièmes
  au-dessus des estimations) ; 2019 et 2020 inchangés ; 2022 lu, 8,2838 au
  lieu de 8,2837. Les niveaux suivent la source : `certifiee` pour 2021, 2022
  et 2026, que la MSA, productrice de la donnée, publie et que le script
  relit ; `haute` pour 2018 et 2020, qu'un rapport parlementaire cite, et
  2023 ; `moyenne` pour 2015 à 2017 et 2019, que le calcul seul donne sur des
  taux lus.
- *L'exemple de la MSA, à défaut d'un assuré.* Aucune publication de la MSA
  ne déroule le calcul d'une pension portée à la PMR et complétée : ni ses
  deux guides « Préparer sa retraite » (2012, 2023), ni ses pages de
  revalorisation, ni la note de sa direction des statistiques au COR (26
  janvier 2023), ni sa synthèse sur la RCO (décembre 2018), ni les Chiffres
  utiles de 2018 et 2023. Ce qu'elle publie en euros se rejoue : la garantie
  d'une carrière complète au 1er janvier 2022, 1 067,91 € par mois, est ce que
  touche un chef de quarante-deux ans parti à 62 ans en 2022 — dans les deux
  moteurs, la carrière ajoutée à leur comparaison — ; les montants mensuels de
  la PMR et de son plafond (681,20 €, 541,30 € et 852,39 € en avril 2013 ;
  699,07 € et 874,76 € en 2021 ; 747,57 € et 961,08 € en janvier 2023) sortent
  des tables au centime inférieur.
- *Les tests* (`tests/test_minima_agricoles.py`, trois de plus) : le calcul
  redonne les montants publiés, le fichier s'en écarte de moins de 0,0002 €
  de l'heure, ses niveaux suivent la source ; les montants mensuels de la
  PMR ; la carrière complète de 2022.

**Ce que la vérification a trouvé.**

- *2024 s'écarte de trois centimes* : 1 177,03 € publiés (Cerfrance, d'une
  page de la MSA qui ne le porte plus), 1 177,00 € calculés. Le script le
  déclare (`ECARTS_CONNUS`).
- *Les « 1 046 € par mois en 2022 »* des Chiffres utiles de la MSA (édition
  2023) sont la garantie de novembre 2021 revalorisée comme les pensions
  servies en janvier 2022, non celle d'une pension prise en 2022 (1 067,91 €).
- *Le guide de 2023* écrit la PMR à 747,54 € par mois ; la note de la MSA au
  COR et le décret, 747,57 €. Le dépôt garde le décret.
- *Le SMIC net de septembre 2023*, que la note du 8 octobre estimait à
  9,0282 € (11,52 € moins les 21,63 %), est ce que le calcul donne.
- *La MSA s'est trompée de SMIC en 2017* : sa page de Guadeloupe dit avoir
  payé en novembre un rappel calculé sur une valeur erronée, puis l'avoir
  récupéré. Aucun montant n'y figure.
- *Les montants mensuels de la PMR de 2013 et de 2021*, au niveau `moyenne`
  dans `pension_majoree_reference.csv`, sont redits par le ministère et la
  MSA ; leur récupérateur, qui écrit ce niveau, n'a pas été touché.

**Ce qui reste**, de cette partie :

1. Un montant de la MSA pour 2015, 2016, 2017 et 2019 : le 820,92 € de 2015
   (73 %), qu'une page de la FDSEA de Lot-et-Garonne aurait écrit et que le
   calcul redonne, n'a pas pu être relu (503) ; les Chiffres utiles de 2016,
   2017, 2019 et 2020, que le site statistique de la MSA ne liste plus.
2. 2023 relu par le script : l'adresse de l'Info presse du 14 février 2023.
3. Un exemple d'assuré de la MSA, s'il en paraît un (simulateur anonyme,
   circulaire).
