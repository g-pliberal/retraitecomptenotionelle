# Étape 17, sixième partie : l'arrondi des services et le minimum garanti, les deux écarts de TRAJECTOiRE

**Le 8 octobre 2026, la demande.** Le propriétaire : « Action 138, étape 17 :
les deux écarts que la confrontation à TRAJECTOiRE laisse ouverts
(tests/test_trajectoire.py, ARRONDI_SERVICES et MINIMUM_GARANTI) : l'arrondi
au trimestre des services de la fonction publique, et le minimum garanti de la
CNRACL du cas type 10. Tranche-les au texte, et corrige le dépôt s'il a tort. »

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ;
fiches `decompte_des_services_fonction_publique` et `minimum_garanti`).

- *Le décompte final.* « Dans le décompte final des trimestres liquidables, la
  fraction de trimestre égale ou supérieure à quarante-cinq jours est comptée
  pour un trimestre. La fraction de trimestre inférieure à quarante-cinq jours
  est négligée » (R. 26 depuis 2004 ; décret n° 2003-1306, article 16, II ;
  décret n° 2004-1056, article 13, III) ; de 1964 à 2003, la fraction de
  semestre de trois mois faisait six mois. La CNRACL : « Il n'y a donc pas lieu
  de procéder à des arrondis intermédiaires », et son exemple, 86 trimestres et
  45 jours, comptés pour 87.
- *La durée de la décote* « est calculée en trimestres et jours sans règle
  d'arrondi » (service des retraites de l'État) ; ses trimestres manquants sont
  « arrondi[s] à l'entier supérieur » (L. 14, I). Le Conseil d'État (2 février
  2010, n° 311495) : l'arrondi de R. 26 ne vaut pas pour la durée de L. 14, mais
  la pension qu'il porte au pourcentage maximum ne subit pas de décote — 155
  trimestres, deux mois et vingt-deux jours, liquidés à 156 et 75 %.
- *Le minimum garanti* : la valeur de l'indice majoré 227 au 1er janvier 2004
  « revalorisé dans les conditions prévues à l'article L. 16 » (L. 17), par
  « années de services effectifs », les bonifications exclues, arrondies comme
  au décompte final (CNRACL, « Les modalités de calcul »).

**Le verdict.**

- *L'arrondi* : les deux modèles ont tort. Le dépôt arrondissait les services
  année par année — au mois et demi sur un relevé, aux trimestres civils
  écoulés sur une carrière reconstituée — et comptait la durée de la décote en
  trimestres entiers ; TRAJECTOiRE n'arrondit rien, proratise sur des tiers de
  trimestre et ne fait aucune décote pour une fraction manquante. Le cas type 6
  de 1955 (dix mois en 1976, sept en 2017) a 166 trimestres au décompte final,
  donc ni décote ni proratisation : le dépôt en comptait 165 et une décote de
  1,25 %, TRAJECTOiRE 165,33/166 sans décote. Les cas types 5, 7 et 11 de 1970
  (un mois de trop peu) ont 171 trimestres et une décote d'un trimestre : le
  dépôt avait raison, par hasard, TRAJECTOiRE tort.
- *Le minimum garanti* : TRAJECTOiRE a tort, sa référence est de 2,28 % sous
  la valeur légale de 2015 à 2023 (1 130,50 € par mois en février 2015 au lieu
  de 1 156,90 €), et il ne sert pas le minimum dû en janvier 2020 au cas type 10
  de 1960 ; le reste de l'écart tient à l'année partagée de la requête, qui ôte
  au relevé du dépôt les mois de fonction publique de l'année d'entrée. Le dépôt
  avait tort aussi : son montant de 2020, 1 174,33 €, revalorisait 2019 de 0,3 %
  au lieu de 1 % ; il projetait sur les prix entre deux montants publiés, à
  l'année (2,9 % de trop en 2019, 4,6 % en janvier 2022) ; il comptait au
  minimum les bonifications pour enfants, que L. 17 exclut.

**Ce qui est fait.**

- *Une fiche datée*, `decompte_des_services_fonction_publique`, en trois
  versions — rien avant le code de 1964, le semestre de 1964 à 2003, le
  trimestre et la durée au jour depuis 2004 —, lue par les deux moteurs
  (`FichesDatees`).
- *Le décompte au jour* (`compter`, `jours_de_la_ligne`,
  `arrondir_les_services`, et leurs jumeaux) : les jours de services des trois
  régimes du code des pensions, année par année, en mois de trente jours, à la
  quotité pour la liquidation ; le décompte final les arrondit une fois ; la
  durée de la décote en garde les fractions (`Durees.ecart_au_jour`), ses
  trimestres manquants arrondis à l'entier supérieur, et la décote s'efface
  quand l'arrondi atteint la durée requise. Le schéma de l'étape passe en
  version 5.
- *Le relevé* : la ligne de la fonction publique dit ses trimestres avec leur
  fraction (« 3.33 » pour dix mois) ; le contexte refuse la fraction d'un autre
  statut. Le script de TRAJECTOiRE écrit désormais ses requêtes ainsi, et celles
  du témoin sont réécrites de même (33 lignes, chacune vérifiée sur l'entier que
  la règle du mois et demi en tirait).
- *Le minimum garanti* : sa référence suit la chaîne des revalorisations des
  pensions civiles jusqu'à la date d'effet, au mois ; elle redonne au centime
  1 248,33 € en juillet 2022 et les montants publiés de 2023 à 2026. Le montant
  de 2020 est retiré du fichier. Il compte les services effectifs arrondis,
  sans les bonifications, depuis 2004.
- *La confrontation* : ARRONDI_SERVICES et MINIMUM_GARANTI ne sont plus
  ouverts, mais déclarés contre TRAJECTOiRE ; le registre porte ses deux
  erreurs.
- *Les tests* (`tests/test_decompte_des_services.py`) : l'arrondi sur les
  exemples de la CNRACL, du Conseil d'État et du service des retraites de
  l'État, au trimestre et au semestre ; le cas du Conseil d'État rejoué au
  mois, sans décote, et en trimestres entiers, avec ; un mois de trop peu ; le
  refus d'une fraction au privé ; la référence du minimum de 2015 à 2026 ; le
  minimum du cas type 10 de 1960 ; cinq requêtes dans les deux moteurs.

**Les mesures.** Le cas type 6 de 1955 : 1,9 % de pension civile de plus,
sans décote, à 166/166. Le cas type 10 de 1960 : 1 064,28 € par mois au
minimum garanti, au lieu de 1 056,90 €. Sur les 763 témoins de simulation, six
bougent au scénario 1, de +0,13 % à +2,61 %, tous d'un trimestre de services
gagné au décompte final, dont l'invalide au minimum garanti en quinzièmes ;
aucun ne baisse. Les deux moteurs concordent sur tous les témoins.

**Ce qui reste.**

- L'article 14 du décret n° 65-773 d'avant 1985, que l'index LEGI ne porte pas.
- La durée tous régimes que le régime général lit garde, pour l'année entamée
  dans la fonction publique, des trimestres entiers ; chercher comment la Cnav
  la compte.
- Les bonifications des emplois classés s'arrondissent à part avant le
  décompte final ; le texte les additionne au jour.
- Le montant de 2020 du minimum garanti au service des retraites de l'État,
  que la DREES donnerait à 1 174,34 €, contre la chaîne.
