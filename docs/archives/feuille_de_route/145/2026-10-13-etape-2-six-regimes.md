# Étape 2, première partie : six régimes que l'action 121 ne touche pas, lus et mis en fiches

**Le 13 octobre 2026 : huit fiches de règles pour six régimes de l'inventaire qui
n'avaient que la fiche générique de liquidation — l'IPACTE, l'IGRANTE, la caisse
des membres du CESE, les gérants de débits de tabac, l'ASV (deux fiches : les
médecins, les quatre autres professions) et les conjoints de commerçants (deux :
leur régime, et celui des entrepreneurs du bâtiment qui partage leur ligne
d'inventaire). Six sont `approchee`, deux `pas_encore_modelisee`, toutes mûres.
Aucun chiffre ne bouge. La lecture trouve cinq écarts au droit que le modèle
porte, dont deux qui déplacent sensiblement des pensions : un rendement double
pour les gérants de débits de tabac, et des annuités du CESE comptées au
pourcentage de l'année de liquidation.**

Demande du propriétaire : « Action 145, étape 2. À ma demande, commence par les
régimes que l'action 121, qui tourne en parallèle, ne touche pas : l'IPACTE et
l'IGRANTE, le CESE, les gérants de débits de tabac, l'ASV, les conjoints
d'Organic. L'outre-mer, le personnel navigant et les assemblées attendent la fin
de l'action 121. » Et : « ce qui devrait s'écrire dans les pages, mets-le dans ta
note ».

- *La méthode.* L'index LEGI et JORF du dépôt, mis à jour au 12 et au 13 octobre
  (aucune rédaction nouvelle à examiner), lu article par article, rédaction par
  rédaction ; les analyses du Journal officiel pour les textes que LEGI ne porte
  pas (le décret n° 51-1445 et ses arrêtés, en grande partie) ; hors de l'index,
  le seul règlement de la caisse de retraites du CESE au 1er janvier 2025, sur le
  site du Conseil (copie datée, empreinte dans la fiche). Légifrance oppose une
  vérification de navigateur à l'outil en ligne de commande.
- *Les fiches.* `ipacte_points` et `igrante_points` (points, partagés par l'année
  des services : services antérieurs validés, cotisations, reprise par
  l'Ircantec en 1971) ; `cese_pension_des_membres` (deux dates qui décident : la
  date du mandat, qui fait le pourcentage de l'annuité, et la première
  désignation, qui ferme la caisse au 1er septembre 2023 ; une version supposée
  pour les vingt-sept jours d'octobre 2010 que le règlement laisse sans taux) ;
  `ravgdt_allocation_viagere` (six versions, de 1963 au taux de 2026) ;
  `asv_medecins_points` et `asv_autres_professions_de_sante` ;
  `organic_conjoints_de_commercants` et
  `entrepreneurs_du_batiment_complementaire`. Elles couvrent les treize réformes
  du calendrier qui nommaient ces régimes sans qu'aucune fiche les couvre, de
  `ipacte_1951` à `carmf_temps_choisi_2017`.
- *Ce que la lecture trouve, et que le modèle ne fait pas.*
  1. **Gérants de débits de tabac : un rendement double.** Le barème du point,
     que la fiche de régime tenait pour « hors index », y est année par année
     depuis 2006 (arrêté du 13 novembre 1963, article 14 : 3,59 € d'achat en
     2005, 4,94 € en 2026 ; 1,99 € de service en 2006, 2,44 € au 1er juillet
     2026), avec le taux de chaque année (décret n° 63-1104, article 2 : 2 %
     jusqu'en 2007, puis de 1,984 % à 1,555 %). Un point y coûte cent fois la
     valeur d'achat en remises corrigées ; le modèle, qui sert 0,49 € de rente
     par euro cotisé (2,42 / 4,94), le fait coûter 4,94 € de cotisation : à
     remises corrigées égales aux remises brutes, il sert le double du droit.
     La correction des remises n'est pas dans l'index : c'est elle qu'il faut
     lire avant de corriger. Ni l'anticipation dès soixante ans (réductions de
     23 % à 6 %), ni les seuils de quinze ans et de 400 points, ni le capital
     sous sept ans ne sont portés.
  2. **CESE : toutes les annuités au pourcentage de la liquidation.**
     `liquider_chaque_regime` prend la période de la fiche de régime en vigueur
     l'année de la liquidation, quand le règlement compte chaque annuité au
     pourcentage de son mandat (2,11 % jusqu'en août 2004, 1,82 % depuis
     octobre 2013) : une liquidation postérieure à 2013 perd 13,7 % sur les
     annuités d'avant septembre 2004, 9,9 % sur celles de 2004 à 2010. Et
     l'allocation viagère des mandats de moins de cinq ans, réduite de moitié
     depuis le 16 novembre 2015, est servie entière.
  3. **IGRANTE : 3,5 % de points en moins.** L'arrêté du 10 mars 1971 majore
     « forfaitairement de 3,50 % » les points de l'IGRANTE avant leur transfert à
     l'Ircantec ; le modèle les sert à la valeur de l'Ircantec et les convertit
     un pour un, et le test `test_un_regime_ferme_ne_vaut_jamais_plus_que_son_successeur`
     borne ce coefficient à 1 : il sera à revoir avec la correction.
  4. **Conjoints de commerçants : des points de l'assuré, non du conjoint.**
     Depuis 2004, les droits de l'ancien régime sont des points portés au compte
     de l'assuré lui-même, au NRCO puis au RCI (règlement du RCI, articles 7, 14,
     15 et 33, annexes 1 et 3), servis avec quinze ans d'assurance avant 2004, ou
     90 points pour l'assuré marié, et réduits selon les pensions du conjoint. Le
     modèle porte la cotisation additionnelle à un rendement nul, au motif que la
     pension va au conjoint.
  5. **IPACTE : des conditions d'affiliation.** Le décret de 1951 réserve l'IPACTE
     à l'ingénieur ou à l'agent de fonctions de catégorie A, payé au moins
     l'indice 225, à temps complet ; le modèle la donne à tout contractuel
     au-dessus du plafond, et lui refuse l'IGRANTE jusqu'à trois plafonds.
  Moindres : les 37,52 points de l'ASV d'avant juillet 1972, la validation des
  services d'avant 1951 et 1960 et leurs points gratuits, l'assiette de l'IPACTE
  jusqu'à 4,75 plafonds depuis 1961, les exclus de l'IGRANTE (les auxiliaires).
- *Ce qui reste à lire.* Les articles de l'IPACTE et de l'IGRANTE que LEGI ne
  porte pas — l'âge, l'allocation, la réversion —, au fac-similé du Journal
  officiel de 1951 et de 1960 ; la correction des remises des débitants ;
  l'article 16 du règlement du NRCO ; les règlements des sections professionnelles
  approuvés le 10 juillet 2026 ; les règlements de 1958 et de 2015 de la caisse du
  CESE. Chaque fiche les nomme dans `sources.a_relire`.
- *Les tests.* Les fiches donnent un statut à trente-quatre rédactions de la liste
  de contrôle des textes (décret n° 70-1277, arrêté du 30 décembre 1970, D. 635-32
  à D. 635-38, D. 645-2 et D. 645-3, L. 645-5, L. 381-32, L. 921-2-1, décret n°
  2011-1644) : le cliquet descend d'autant, à 9 777 après le rebasage sur
  `main`. `test_carte.py` et
  `test_textes.py` passent, et la suite rapide.
- *Ce qui devrait s'écrire dans les pages*, pour la session qui les tient. Aucune
  page ne cite ces régimes en dur : le compte des fiches et la carte se refont
  d'eux-mêmes. Deux choses, si elle le juge utile : la page des limites (ou
  Méthode) pourrait nommer les deux écarts qui déplacent des pensions, le
  rendement des gérants de débits de tabac et les annuités du CESE ; et la ligne
  d'inventaire des gérants de débits de tabac, que la page Données affiche, dit
  le barème du point « hors index », ce qui est faux depuis 2006 — sa correction
  est une donnée (`regimes/gerants_debits_tabac.yaml`, `manque`), à faire avec la
  modélisation plutôt que dans les pages.
- *Ce qui ne change pas.* Aucun moteur, aucune fiche de régime, aucun témoin. Les
  cinq écarts sont des changements du modèle, hors de l'action 145, qui
  documente sans calculer : au propriétaire de dire s'ils ouvrent une action.
- *Ce qui reste de l'étape 2.* L'outre-mer, le personnel navigant et les
  assemblées, à la fin de l'action 121 ; puis les hors champ dont des assurés
  vivent encore (Crédit foncier, ORTF, CRFOM) ; puis les limites de l'étape
  (`docs/limites/4-regimes-incomplets.md`), une fois, à sa fin.
