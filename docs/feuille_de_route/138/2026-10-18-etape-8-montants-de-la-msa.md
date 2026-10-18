# Étape 8, treizième partie : un montant de la MSA pour 2015 à 2017 et 2019, cherché d'ici sans être trouvé

**Le 18 octobre 2026, la demande.** Le premier reste de l'étape, dans l'ordre
du bloc « Reprise » : « un montant de la MSA pour 2015-2017 et 2019 », la
garantie mensuelle d'une carrière complète de chef (73, 74, puis 75 % du SMIC
net agricole), que `complement_differentiel_rco.csv` ne tient, pour ces quatre
années, que du calcul (`moyenne`). Session du lot 4 de la vague du 17-18
octobre, sur les données.

**Ce qui a été lu**, le 18 octobre (journal de veille du jour).

- *La MSA*, sur statistiques.msa.fr : les Chiffres utiles nationaux de 2015 à
  2021 (2015 et 2016 en archive zip, que la note du 14 octobre croyait
  retirés), l'Infostat des retraites des non-salariés de 2015, les bilans de
  2016 et 2017, les prévisions de 2015-2019 à 2017-2021, l'étude des
  inégalités de pension de 2018, dix-huit tableaux de bord trimestriels des
  retraites des non-salariés, de 2015 à 2020 ; la page de la MSA
  Mayenne-Orne-Sarthe sur le versement de 2015. Tous écrivent 73, 74 puis
  75 % du SMIC net, des effectifs et des montants moyens, jamais la garantie
  en euros.
- *Le Sénat* : les seize tomes des rapports de la commission des affaires
  sociales sur les PLFSS de 2016 à 2020, rien ; le rapport n° 315
  (2017-2018), 2018 seul ; toutes ses questions écrites (dump de
  data.senat.fr du 18 octobre) : le ministère ne répond qu'en pourcentages ;
  les sénateurs écrivent 833, 840, 841 ou 852 euros, et en 2019 les 871 de
  2018.
- *L'Assemblée* : les réponses n° 97094 (XIVe législature), 4055, 5154 et
  40458 (XVe), des pourcentages, et un trop-perçu d'au plus 41,21 € par mois
  en 2017 ; le rapport n° 4403 (janvier 2017) et la première séance du
  2 février 2017, sur la proposition de loi Chassaigne ; le rapport n° 3071,
  2020 seul ; l'étude d'impact du projet de loi instituant un système
  universel de retraite (janvier 2020), dont le tableau des minima au
  1er janvier 2019 écrit « 75 % du SMIC agricole », sans montant.

**Ce que la vérification a trouvé.**

- *Aucun montant de la MSA pour ces quatre années ne se lit d'ici.* Ses
  publications statistiques ne l'écrivent pas ; ses pages et ses communiqués
  de 2015 à 2019 ne sont plus en ligne, et l'archive du web, qui les garde
  peut-être, est refusée par le réseau de la session. Le site de la DREES ne
  répond pas (503) ; le dump des questions écrites de l'Assemblée se coupe à
  35 Mo.
- *2015, à l'euro, par des tiers* : « 73 % du SMIC, soit 820 euros »
  (M. Arnaud Viala, compte rendu de la première séance du 2 février 2017), et
  « 73% du SMIC net (820 euros) en 2015 » (Agri 46, 23 juin 2016) ; le calcul
  donne 820,92 €. La page de la FDSEA de Lot-et-Garonne, qui écrirait
  820,92 €, répond 403. La ligne reste `moyenne` : une déclaration en séance
  n'est pas un rapport que la commission tient de la caisse, et la même
  séance chiffre 2017 à 840 ou 860 euros.
- *2017 n'est publié que faux* : les 860,30 euros du rapport n° 4403
  (M. Michel Issindou), les 840 et 860 euros de la séance ne redonnent pas la
  garantie de la MSA, 854,91 € par le calcul.
- *L'étude d'impact de 2020* écrit aussi « 945 € bruts par mois » pour une
  carrière complète : ni 2019 (894,13 €) ni 2020 (904,83 €), et rien ne dit
  d'où ce montant vient.
- *Rien ne bouge* : ni fichier, ni chiffre, ni niveau.

**Ce qui reste**, de l'étape, dans l'ordre du bloc « Reprise » :

1. Au propriétaire, depuis un poste qui atteint l'archive du web : les pages
   de la MSA sur la garantie de 2015 à 2019 (communiqués de novembre 2015,
   pages de revalorisation de janvier 2016, 2017 et 2019), et la page de la
   FDSEA de Lot-et-Garonne. Un montant trouvé entre dans `PUBLIES` de
   `scripts/fetch/msa_smic_net_agricole.py`, sa ligne au niveau que le test
   exige.
2. Inchangés : le 2° de D. 732-110, II (décès du conjoint, à saisir) ; la PMR
   revue quand les ressources changent ; la durée de chef reconstituée de
   D. 732-110, III ; les points 2 et 3 de « Ce qui reste » de la note
   « points des conjoints ».
3. À la fin de l'étape, dans la fiche `complement_differentiel_rco` : sa
   première approximation et son premier `a_relire` datent d'avant le
   14 octobre, qui a expliqué les 0,79 point et lu 2018, 2020 et 2022.
4. Au propriétaire, inchangé : les seize points d'une année de conjoint
   d'avant 1999.
