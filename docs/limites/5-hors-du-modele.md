# 5. Ce que le modèle ne calcule pas, et pourquoi

Ce qui suit n'est pas une liste de manques mais un **périmètre**, et chaque
ligne dit ce qu'elle coûte et dans quel sens. Une limite qu'on sait mesurer
n'est plus une limite : c'est un paramètre connu du résultat.

- **La grille de cas types ne sait pas compter le coût d'un avantage non
  contributif, et le sens de l'erreur est connu : elle n'a pas d'enfants.** Un
  seul des treize cas types en a — `carriere_interrompue`, deux enfants —, si
  bien que la majoration de pension pour trois enfants et plus valait **zéro
  toutes les années de la série**. La surcote parentale, elle, la grille la
  sert à la carrière interrompue à partir de la génération 1970, mais elle ne
  paie que des pensions prenant effet à compter de 2026 : rien à mesurer sur
  les années publiées. La grille est faite pour comparer des systèmes sur une même
  carrière, où les erreurs de niveau s'annulent au dénominateur ; le coût d'un
  avantage est un compte de POPULATION. C'est l'erreur déjà rencontrée sur la
  garantie vieillesse, que les cas types surestimaient de loin et que le barème
  appliqué à la distribution DREES chiffre juste.

  **La limite tient toujours, mais elle ne mord plus sur le chiffre publié**,
  parce que le chiffre publié n'est plus calculé. Les avantages non contributifs
  valent <!--chiffre:mesure(avantages?annee=2024)-->97,6<!--/--> milliards en 2024, soit <!--chiffre:mesure(avantages?annee=2024&quoi=part_depense)-->22,9<!--/--> % de la dépense, et **<!--chiffre:mesure(avantages?annee=2024&quoi=part_lue)-->84<!--/--> % de ce
  total est LU** : la réversion dans l'enquête de la DREES auprès des caisses,
  et dix autres lignes dans les sous-postes des Comptes de la protection
  sociale, dont la majoration pour enfants à <!--chiffre:mesure(avantages?annee=2024&quoi=ligne&cle=majoration_enfants)-->7,8<!--/--> milliards — que le modèle
  chiffrait à zéro. Le COR chiffre l'ensemble des droits de solidarité à « de
  l'ordre d'un cinquième » : on y est. Ce que le modèle apporte n'est donc pas
  le chiffre mais la LISTE, et les <!--chiffre:mesure(avantages?annee=2024&quoi=calculees)-->15,5<!--/--> milliards qu'il calcule encore lui-même
  restent soumis à cette limite. Vingt-sept dispositifs sur quarante-cinq ne
  portent aucun chiffre, chacun avec sa raison écrite.

  **Une seconde limite, découverte en réparant la première : les deux mesures
  n'ont pas la même fenêtre.** Les sous-postes des comptes ne sont publiés que
  depuis 2020, la réversion depuis 2004, et le modèle calcule depuis 1959. Une
  ligne ne mélange donc jamais les deux périmètres — la règle a été posée après
  qu'un minimum vieillesse eut valu <!--chiffre:illustration()-->0,02<!--/--> milliard en 2019 par le modèle et 4,01
  en 2020 par les comptes, dans la même série. Le site porte en conséquence
  deux tracés qui ne s'additionnent pas : le NIVEAU sur cinq ans, la FORME sur
  soixante-six. Voir `docs/avantages_non_contributifs.md`.

- **Le diviseur est le même pour tout le monde, et il transfère à qui vit
  plus longtemps — le système actuel autant que les autres.** Ce fut la règle
  jusqu'au 21 septembre 2026 : l'espérance de vie du §5 de `methodologie.md`
  était alors celle de la population générale. Les
  pensionnés civils de l'État vivent un an de plus à 65 ans, d'après leur
  propre régime ; les 5 % d'hommes les plus aisés vivent sept ans de plus à
  65 ans que les 5 % les plus modestes, d'après l'INSEE. Depuis le
  20 septembre 2026, les deux écarts sont MESURÉS
  (`scripts/mortalite_population.py`, action 14) — et, depuis le
  21 septembre 2026, le diviseur par vingtile de niveau de vie est le DÉFAUT
  du modèle, stock compris, sur tous les chiffres du site ;
  `population_conversion=None` rend la table commune, et les chiffres
  ci-dessous sont mesurés contre elle. Pour le fonctionnaire sédentaire né en 1975, la
  table de sa population lui donne 1,5 an de rente de plus que la table
  commune, soit 5,7 % de pension notionnelle à capital égal et 54 000 € sur
  la vie sous le système actuel, dont la pension ne bouge pas d'un euro parce
  qu'aucun diviseur ne l'a calculée. Par le revenu, chaque cas type rattaché
  au vingtile de niveau de vie où son salaire le place : le salarié au SMIC a
  3,0 ans de rente de moins que la table commune ne lui en compte et
  l'exploitant agricole 3,7 de moins, le cadre 2,7 de plus et le libéral 3,1
  de plus — 49 000 € retirés au premier, 186 000 € ajoutés au dernier (3,2
  ans et 173 000 € avant que la règle de départ du libéral ne change, le
  22 septembre 2026), sur la
  vie et sous le système actuel. Le diviseur commun transfère donc des
  modestes vers les aisés, dans le sens qu'on craignait, puisque qui vit
  longtemps est aussi qui a le plus cotisé ; et ce n'est pas un défaut du
  notionnel, toute rente viagère à taux commun le porte, le droit en vigueur
  le premier. Ce que la mesure suppose est écrit avec elle : un rattachement
  par le salaire là où l'INSEE mesure un niveau de vie de ménage, un facteur
  constant dans le temps, une espérance de stock appliquée à des liquidants
  futurs, et une grille de cas types qui n'est pas une population. Ce que
  ce transfert coûte au régime se mesure aussi (`--deficit`) : un diviseur
  par vingtile baisserait la dépense des scénarios notionnels de 3,5 à
  4,4 %, de deux à cinq dixièmes de point de PIB de solde moyen, parce que les gros capitaux
  sont servis le plus longtemps. La page
  Coût l'applique depuis lors par les pensions de ses cas types, mais compte
  encore tout le monde à la mortalité générale : ce sous-compte déplace son
  rapport de masses de moins de 1 %, un dixième de point de PIB au plus en
  2070, et ne se corrigerait proprement qu'avec la distribution des pensions
  par niveau de vie.

- **La décote surpunit l'anticipation ordinaire et sous-punit l'extrême.**
  Mesuré en comparant ce que coûte une année d'anticipation sous le droit en
  vigueur et sous le coefficient de conversion notionnel, sur un fonctionnaire
  sédentaire de la génération 1965 : partir deux ans plus tôt laisse 81,7 % de
  la pension sous le droit actuel contre 84,1 % sous le notionnel — le droit est
  PLUS DUR de 2,4 points ; à cinq ans d'avance, plus dur de 7,0 points. Puis la
  décote bute sur son plafond de vingt trimestres et le rapport s'inverse : à
  huit ans d'avance le droit est plus doux de 0,8 point, à dix ans de 4,2, à
  douze ans de 6,4. Or l'anticipation extrême est exactement celle de la
  catégorie active, de la super-active, de la conduite SNCF et des militaires :
  le barème est le plus clément là où il devrait l'être le moins. Voir
  `docs/avantages_non_contributifs.md` §4 ter.

- **Une décote plafonnée ne sait pas dire qui part trop tôt, et le modèle en
  hérite.** L'article L. 14 borne la décote à vingt trimestres : un agent de
  catégorie active parti à <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active&generation=1960)-->57<!--/--> ans et un agent sédentaire parti le même jour
  butent tous deux sur le même plafond, et leurs pensions ne diffèrent que de
  quelques centaines d'euros par an pour la génération 1960 — la page Avantages
  en donne le chiffre, que le modèle calcule depuis le 22 septembre 2026 ; le
  chiffre que cette page et le site portaient en dur avait dérivé deux fois
  sans que rien ne le dise. Pour la génération 1965 l'écart tombe sous la centaine d'euros, le classement abaissant
  par ailleurs la durée requise d'un trimestre. Mesurer la
  valeur d'un avantage d'ÂGE par l'écart de MONTANT à date de départ fixe donne
  donc un chiffre petit — <!--chiffre:mesure(avantages?annee=2024&quoi=ligne&cle=categorie_active)-->0,7<!--/--> milliard en 2024 pour la catégorie active — et ce
  chiffre n'est pas faux, il est incomplet. Il porte de surcroît, depuis le
  22 septembre 2026, la durée requise propre aux emplois classés, que le
  contrôle d'isolement de `avantages.py` accepte pour ce seul avantage
  (`DUREE_REQUISE_EST_L_AVANTAGE`), le texte la donnant « au titre de la
  catégorie active ». Ce que l'avantage coûte, ce sont les annuités
  servies avant l'âge légal, que nulle décote ne rattrape. Elles valent **<!--chiffre:mesure(avantages?annee=2024&quoi=anticipees)-->11,4<!--/--> milliards en 2024**, dont <!--chiffre:mesure(avantages?annee=2024&quoi=anticipees&motif=classement)-->7,2<!--/--> pour le
  classement, <!--chiffre:mesure(avantages?annee=2024&quoi=anticipees&motif=regime_special)-->2,3<!--/--> pour les régimes spéciaux et <!--chiffre:mesure(avantages?annee=2024&quoi=anticipees&motif=carriere_longue)-->1,9<!--/--> pour la carrière longue
  (`scripts/cout_avantages.py --duree`). Ce sont des annuités anticipées et non
  un surcoût net — partir tôt, c'est aussi cotiser moins et mourir plus tôt en
  moyenne ; c'est exactement l'arbitrage qu'un coefficient de conversion
  notionnel rend automatique et que le droit actuel ne rend nulle part.

- **Le pilotage, et non plus le solde.** Le modèle calcule des droits
  individuels ; il porte une pyramide des âges, qui lui dit ce que chaque
  système COÛTERAIT ; il porte depuis peu les RESSOURCES, et donc le solde et le
  **coefficient d'équilibre** de chaque système, année par année, de 2002 à
  2070. Ce qui lui manque encore est le cran suivant : APPLIQUER ce
  coefficient. Un système notionnel réel l'applique, et d'abord à la baisse :
  la Suède freine les comptes et les pensions dès que son indice d'équilibre,
  un rapport de stocks et non de flux, passe sous un ; l'excédent, lui, a
  longtemps dormi — <!--chiffre:illustration()-->15<!--/--> % encore pour 2027 (indice de 1,1472,
  Pensionssystemets årsredovisning 2025) —, jusqu'à l'« accélérateur » que
  son groupe des pensions a décidé le 26 août 2025 et que la loi 2026:1301
  déclenche au-delà de 1,15. Le modèle
  calcule ce facteur et ne l'applique jamais : toutes les courbes de coût de la
  page **Coût** sont celles d'un système qui ne se pilote pas. Le facteur étant
  commun, l'appliquer déplacerait les niveaux sans toucher aux ÉCARTS ENTRE
  CARRIÈRES, qui sont l'objet du modèle — mais il déplacerait bel et bien les
  niveaux, et un coefficient de <!--chiffre:mesure(coefficient?scenario=3)-->1,69<!--/--> en 2070 pour le scénario 3 ne se lit donc
  pas comme une économie de <!--chiffre:mesure(coefficient?scenario=3&quoi=economie)-->41<!--/--> % : il se lit comme la marge dont ce système
  disposerait pour servir davantage à prélèvement inchangé.

- **Les ressources ne sont pas celles du risque vieillesse, et ne peuvent pas
  l'être.** Les Comptes de la protection sociale, d'où vient toute la dépense du
  dépôt, NE VENTILENT PAS LEURS RESSOURCES PAR RISQUE : ils publient la dépense
  risque par risque et le financement de l'ensemble, maladie et famille
  comprises. Une « recette du risque vieillesse » n'a pas de définition
  comptable, les cotisations d'un régime polyvalent n'étant affectées à aucun
  risque. Le solde vient donc d'un autre compte et d'un autre périmètre : celui
  du COR — régimes légalement obligatoires, FSV compris, RAFP exclu —, dont on
  prend les DEUX colonnes, dépenses et ressources, pour ne pas soustraire deux
  périmètres. Les deux se recoupent à moins de trois dixièmes de point de PIB
  (<!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2024&poste=depenses)-->13,86<!--/--> % contre <!--chiffre:mesure(depense?annee=2024&quoi=part_pib_repartition)-->13,59<!--/--> % en 2024, <!--chiffre:mesure(depense?annee=2024&quoi=cor)-->407<!--/--> contre <!--chiffre:mesure(depense?annee=2024&quoi=repartition)-->398,8<!--/--> Md€), ce qui
  vaut contrôle et non identité ; seul
  le RAPPORT des masses, qui est sans dimension, passe de l'une à l'autre. Ce
  compte vaut `haute` et jamais `certifiee` : le COR consolide des comptes
  produits par les régimes, c'est le critère 1 du manifeste des sources.

## Le reste du périmètre

- **Les contributions d'équilibre de l'Agirc-Arrco ne vont pas au compte
  notionnel, et c'est un choix.** La contribution d'équilibre général et la
  contribution d'équilibre technique depuis 2019, l'AGFF de 2001 à 2018 et
  l'ASF avant elle sont prélevées sur les salaires du privé, au salarié et à
  l'employeur, sans ouvrir de points. Ce ne sont pas des cotisations, mais des
  contributions que l'accord du 17 novembre 2017 institue « dans une
  perspective de financement des opérations du régime » (article 37) : le
  compte, qui reçoit toutes les parts des cotisations — la majoration du taux
  d'appel, la cotisation déplafonnée du régime général —, ne les reçoit pas, et
  le taux du régime unique les omet de même. Voir, dans la feuille de route,
  « Ce qui est délibérément en bas ».
- **Le chômage aux complémentaires, approché.** Le scénario 1 sert les points
  d'une année chômée sur le salaire d'avant l'interruption, borné à quatre
  plafonds, aux taux d'une année travaillée pour l'allocation d'assurance et à
  ceux de la solidarité — <!--chiffre:valeur(data/reference/legislation/chomage_complementaires.yaml:solidarite.taux.agirc_arrco.taux*100)-->4<!--/--> %, ou
  <!--chiffre:valeur(data/reference/legislation/chomage_complementaires.yaml:solidarite.taux.agirc.taux*100)-->8<!--/--> et <!--chiffre:valeur(data/reference/legislation/chomage_complementaires.yaml:solidarite.taux.agirc_entreprises_nouvelles.taux*100)-->12<!--/--> % à l'Agirc
  avant 2019 — pour l'allocation de solidarité spécifique ; le compte notionnel
  ne porte que ce qui a été versé : <!--chiffre:valeur(data/reference/legislation/chomage_complementaires.yaml:assurance.part_cotisation*100)-->60<!--/--> %
  de la cotisation et <!--chiffre:valeur(data/reference/legislation/chomage_complementaires.yaml:assurance.participation_reversee*100)-->0,8<!--/--> % de
  l'assiette par l'Unédic, <!--chiffre:valeur(data/reference/legislation/chomage_complementaires.yaml:solidarite.versement*100)-->70<!--/--> % de la
  cotisation de solidarité par l'État, et aux scénarios 2 et 3 la participation
  de l'allocataire. La préretraite du FNE a les taux de la solidarité, garantie
  minimale de points comprise, sur un salaire borné à deux plafonds, et ceux de
  l'assurance quand sa convention est d'avant 1984 ; le salarié agricole n'a
  rien avant le 1er avril 1974, le salarié calédonien jamais rien, la CAFAT et
  non l'Unédic indemnisant son chômage ; et l'indemnisation cesse à l'âge d'annulation
  de la décote, et depuis le 1er avril 1983 à l'âge légal pour qui a la durée
  requise (L. 5421-4 du code du travail) : les années de chômage d'après ne
  valent plus rien, et celle de la coupure s'arrête au mois qui la précède
  quand elle couvre l'année entière. Les lignes ne disent ni la date de la
  rupture, que l'Arrco regarde pour la solidarité, ni celle de la convention
  du FNE : le modèle les prend au premier millésime du chômage ou de la
  préretraite. Il ne connaît ni les jours de différé, ni le salaire de
  référence calculé sur vingt-quatre mois, ni le taux d'une entreprise qui
  cotisait au-dessus du minimum, ni le premier jour propre aux départements
  d'outre-mer, en 1980 ; la préretraite progressive et l'activité partielle ne se saisissent
  pas, l'Ircantec sans cotisations et les conventions de la CNBF et de la CRPN
  avec l'Unédic ne sont pas portées, et la durée de l'allocation d'assurance
  n'est bornée que par la coupure : la saisie dit ce qui a été versé. Les
  fiches `chomage_retraite_complementaire`, `financement_chomage_complementaire`
  et `fin_indemnisation_chomage` en tiennent la liste.
- **Les services passés de l'outre-mer, approchés.** L'Arrco n'est obligatoire
  en Nouvelle-Calédonie que depuis 1995, à Saint-Pierre-et-Miquelon que depuis
  1988 : les années d'avant y sont des services passés, que l'institution valide
  sans cotisation. Le scénario 1 leur sert les points d'une année cotisée de
  métropole, à une pension prise depuis la généralisation, quand le droit les
  calcule au taux de l'adhésion, et selon une pesée démographique pour les
  anciens salariés et les retraités ; une pension calédonienne prise avant 1995
  n'a pas d'Arrco, et la révision qui a servi aux retraités, à la
  généralisation, leurs services passés n'est pas portée ; le compte notionnel
  n'en porte rien. Le modèle ne connaît pas l'employeur qui cotisait déjà, ni
  ce que la CAFAT reconnaît. La fiche `services_passes_outre_mer` en tient la
  liste.
- **L'horizon de la projection.** La dépense observée s'arrête à 2024,
  dernière année publiée par la DREES ; la trajectoire projetée s'arrête à
  2070, dernière année des projections de population de l'INSEE. Ni l'une ni
  l'autre de ces bornes n'est une décision du dépôt : ce sont celles des
  sources. Au-delà de 2070, le dépôt ne dit rien, et le COR non plus.

- **Les comportements.** Les âges de liquidation sont ceux que l'utilisateur
  déclare. Or une réforme qui pénalise fortement les départs précoces conduit à
  les décaler. Le sens du biais est connu : les écarts affichés sont des effets
  **à comportement inchangé**, et ils surestiment donc la perte réelle — un
  assuré qui, dans un système notionnel, travaillerait deux ans de plus
  récupérerait à la fois des cotisations et un diviseur plus favorable.

- **Le net.** Le modèle calcule en **brut**, et le site convertit en net ce
  qu'on touche — la pension, le salaire —, saisie comprise. La conversion
  suppose ce que le §5 ante ter décrit : un taux de CSG sur les pensions qui
  est celui du taux plein pour tout le monde, faute de connaître le revenu
  fiscal du FOYER, que le modèle ne connaît pas puisqu'il décrit une carrière
  et non un ménage. Ce prélèvement étant proportionnel et identique dans tous
  les scénarios, il ne déplace aucun des écarts affichés.

- **L'arrondi des revenus portés au compte.** L'article L. 133-10 du code de
  la sécurité sociale arrondit à l'euro le plus proche « le montant des
  cotisations et contributions sociales et de leurs assiettes » — donc les
  revenus inscrits au compte, la fraction de <!--chiffre:illustration()-->0,50<!--/--> € étant comptée pour 1. Le
  modèle ne l'applique pas : il porte au compte des revenus reconstitués, au
  centime. L'écart est borné et il est petit — chaque année retenue s'écarte de
  <!--chiffre:illustration()-->0,50<!--/--> € au plus, donc leur moyenne aussi, donc une pension au taux plein de
  **<!--chiffre:illustration()-->0,25<!--/--> € par an** au plus, soit **<!--chiffre:illustration()-->0,02<!--/--> € par mois**, quel que soit le niveau
  de revenu. Deux
  raisons de ne pas l'appliquer aujourd'hui : la règle vise des assiettes
  DÉCLARÉES, que le modèle n'a pas — il synthétise ses revenus depuis un profil
  —, et la doctrine ne dit pas si l'arrondi précède ou suit la revalorisation,
  ce qui n'a aucun effet sur le résultat mais en aurait un sur ce qu'on pourrait
  affirmer. Le reste de la chaîne, lui, est conforme : les trimestres sont
  arrondis à l'entier supérieur (R. 351-27), et la pension n'est pas arrondie du
  tout — voir `methodologie.md`.

- **La capitalisation.** Le compartiment RAFP est isolé et servi à son propre
  barème, identique dans les six scénarios et sorti des totaux de la
  répartition (§3), mais son **rendement financier propre** n'est pas
  modélisé : ses points sont valorisés au barème publié par l'ERAFP,
  non par le rendement de son portefeuille. C'est le traitement demandé — seule
  la répartition est en cause — et il rend le RAFP comparable au reste plutôt
  que de le faire dépendre d'hypothèses de marché.

- **Les carrières réelles.** Une carrière se décrit de deux façons, et la
  seconde n'est plus réservée au Python : le **profil paramétrique** — des
  métiers, un niveau de revenu relatif, une progression —, ou le **relevé**
  saisi année par année dans le champ prévu du simulateur, qui n'en reconstitue
  rien. Il reste à ce chemin une approximation, une convention et une
  impossibilité.

  L'approximation est le MOIS. Un relevé donne l'année, jamais le mois : chaque
  ligne vaut donc une année civile pleine, sauf celle du départ, que la date de
  liquidation tronque parce que le modèle la connaît. L'année d'entrée dans la
  vie active reste comptée pour une année entière alors qu'elle est presque
  toujours partielle — son revenu est celui des mois travaillés, et le modèle ne
  peut pas l'annualiser sans savoir lesquels. Un régime liquidant sur les six
  derniers mois de service n'en souffre pas, cette année-là n'étant pas la
  dernière ; un régime qui prend les vingt-cinq meilleures années y voit une
  année faible de plus, exactement comme le droit.

  La convention est l'AVENIR. Un relevé s'arrête à sa dernière année ; le site
  le poursuit jusqu'au départ, comme le dernier métier d'un parcours court
  jusqu'à lui et comme l'estimation officielle prolonge les revenus — décision
  du propriétaire, le 4 octobre 2026 : jusque-là, qui déposait son relevé à
  quarante ans recevait la pension de qui cesserait de travailler le jour
  même. La convention est celle du report de la proposition (§ 4, « L'âge
  légal de la proposition ») : la dernière année se prolonge, son statut et la
  nature de sa période, son revenu avancé au rythme du salaire moyen, l'année
  du départ au prorata de ses mois, les trimestres déduits du revenu
  (`prolonger_releve`, `Contexte.releve_prolonge`). Les années ajoutées
  prennent le motif que la saisie leur donne, comme celles d'une carrière de
  métiers : une période à l'étranger les vide, le champ « Interruptions »
  garde le dernier mot, et qui ne travaille plus les y déclare
  `sans_activite`, ce que la page lui propose — il retrouve alors, dans les
  six scénarios, la pension de son relevé arrêté. La retraite progressive les
  met à temps partiel ; la radiation pour invalidité d'un fonctionnaire les
  arrête à sa date. Rien ne s'ajoute à qui est parti une année déjà passée :
  son relevé dit toute sa carrière.

  L'impossibilité reste l'INTERROGATION AUTOMATIQUE du répertoire de gestion
  des carrières uniques : il n'est pas ouvert au public, et son accès passe par
  une authentification personnelle qu'un script ne saurait porter sans détenir
  les identifiants de l'assuré. Ce qui a cédé, en revanche, c'est la recopie à
  la main : **le relevé se dépose maintenant en PDF sur le simulateur**, qui le
  lit dans le navigateur — il est téléchargé par l'assuré sur son compte
  retraite, et le fichier ne quitte pas la page. `moteur/js/lecture-pdf.js` en
  tire les lignes de texte, `moteur/js/releve-lu.js` la carrière, et le champ
  `releve` reçoit ce que l'un et l'autre ont compris. Restent quatre choses que
  le document lui-même ne donne pas, et que le site dit à qui le dépose :

  - **Le revenu du relevé du régime général est plafonné.** La caisse ne
    reporte au compte que la part du salaire brut qui tombe sous le plafond de
    la Sécurité sociale : au-delà, ce relevé n'affiche pas le salaire en
    entier, et la simulation lit donc un revenu tronqué. Le relevé tous
    régimes qu'info-retraite délivre en 2026 porte, lui, le « revenu
    d'activité soumis à cotisations retraite », plafond franchi compris, et la
    lecture ne le dit pas plafonné. La carrière paramétrique ne l'est pas.
  - **Un régime qui compte en points ne porte aucun revenu.** Les professions
    libérales depuis 2004, les exploitants agricoles : leur relevé donne des
    points et des trimestres. La lecture prend les années et les trimestres,
    laisse le revenu à zéro et le dit — déduire un revenu du barème de la
    caisse serait écrire un chiffre que le document ne porte pas.
  - **Un état de services couvrant plusieurs années n'est pas réparti.** « Du
    01/09/1996 au 31/08/2001 », tel que la fonction publique l'écrit, ne dit ni
    le revenu de chaque année ni leur partage : la ligne ressort telle quelle
    et reste à saisir.
  - **Le document doit se reconnaître.** Un fichier qui ne porte ni le titre
    d'un relevé ni l'en-tête de la colonne des trimestres n'est pas lu du tout.
    C'est un vrai document qui l'a imposé : le rapport de l'OPEF sur les frais
    de l'épargne retraite, cent pages sans le moindre relevé, rendait
    vingt-deux « années de carrière » qui n'avaient jamais existé.

  Et un PDF qui n'est qu'une image — un scan, une photographie, une capture
  d'écran — ne porte aucun texte : rien ne s'y lit, et la page le dit plutôt
  que de rendre une carrière vide sans explication.

  **Ce qu'un vrai document a appris, le 22 septembre 2026 — et ce qu'il ne
  prouve pas.** La lecture avait été écrite contre des relevés d'essai, faute
  d'en avoir un vrai : aucun n'est public. La première estimation retraite
  déposée sur le site a corrigé quatre défauts d'un coup, et c'est elle qui fixe
  désormais les règles de lecture. **Ce document n'était pas intact** : produit
  par le composeur d'Info Retraite (`KslPrn`), il avait été rouvert dans une
  suite bureautique (`ONLYOFFICE 9.4`) pour être anonymisé, puis ré-exporté. Ce
  qui vient de la caisse et ce qui vient de l'éditeur se sépare donc, et il faut
  le séparer :

  - **De la caisse, et vérifiable comme tel** : les deux tableaux et leurs
    en-têtes, les colonnes, les unités écrites, la note de bas de tableau, le
    pied de page daté, les projections de départ. C'est le CONTENU, et c'est de
    lui que viennent les règles de lecture du relevé.
  - **De l'éditeur, ou probablement de lui** : les polices du fichier — du
    Calibri, qu'aucune administration n'emploie —, donc la table `ToUnicode` et
    la forme de ses plages ; et la couche de doublure, où le texte d'une page
    entière est collé bout à bout. Les deux défauts du lecteur de PDF ont été
    trouvés là, et les corriger est juste — la forme tableau d'un `bfrange` est
    de la norme, et le texte tourné existe partout — mais **rien ne dit encore
    qu'un document intact d'Info Retraite les aurait exigés**.

  Ce jour-là, le relevé n'avait été confronté à aucun PDF de caisse INTACT. Ce
  qui a été vérifié sur celui-ci est que la carrière s'en lit en entier, et le
  contrôle vient du document lui-même : le total de trimestres enregistrés qu'il
  annonce en synthèse est exactement celui que la lecture recompose, année par
  année, depuis l'autre tableau. Le chiffre est sous l'action correspondante de
  la feuille de route : il appartient à un document qui ne peut pas être publié,
  et aucune sonde du dépôt ne saurait donc le recalculer.

  - **Un relevé porte deux tableaux, et ils se complètent.** L'un donne les
    trimestres année par année et ne porte aucun revenu ; l'autre donne les
    revenus par PÉRIODE — « 01/01/2025 31/12/2025 49 150 € » — et ne porte
    aucun trimestre. Une année se lit donc dans les deux à la fois.
  - **L'unité écrite l'emporte sur la position.** « 4 trim. », « 203,91 pts »,
    « 49 150 € » : une caisse écrit toujours ce que ses nombres sont, et s'y
    fier vaut mieux que de deviner une colonne. C'est ce qui permet de prendre
    à une ligne d'Agirc-Arrco sa durée sans prendre ses points pour un revenu —
    et de compter une période que seule la complémentaire a reportée.
  - **Un document mêle à sa carrière des lignes qui lui ressemblent.** Un pied
    de page daté, une valeur du point à une date, une phrase française qui
    porte une année, un montant et des trimestres, et des projections de départ
    en 2060. Quatre règles les écartent : une période a deux bornes, une ligne
    de tableau n'est pas une phrase, une ligne de tableau porte quelques
    nombres et non quarante, et un relevé ne rapporte jamais l'avenir.
  - **Un PDF peut porter deux fois le même texte** : une couche visible, mise
    en page, et une couche de doublure où toute une page est collée bout à
    bout. Additionnée à la première, elle faisait des revenus de deux millions
    d'euros. Celle-ci venait de la suite bureautique ; un document rouvert pour
    être anonymisé, ou simplement ré-enregistré, en porte une.

  **Ce qu'un relevé intact a appris, le 4 octobre 2026.** Le relevé de
  carrière qu'info-retraite délivre en 2026, téléchargé par l'assuré et lu
  sans être rouvert, sort du même composeur (`KslPrn`). Il confirme le texte
  tourné — un tampon dans la marge de chaque page — et a montré quatre choses
  de plus, que la lecture suit désormais :

  - **Le repère de ses pages est retourné.** Chaque page s'ouvre sur une
    matrice `cm` qui place l'origine en haut de la feuille, et certaines pages
    sont coupées en plusieurs flux, un opérateur commencé dans l'un s'achevant
    dans le suivant. Lu sans ce repère, le texte sortait du bas vers le haut,
    et chaque ligne d'un bloc prenait le régime du bloc du dessous.
  - **Une même paie peut y figurer deux fois.** Quand la base et l'Agirc-Arrco
    ne la voient pas tout à fait de même, le relevé porte, sous le même
    employeur, une ligne qui ne nomme que « L'Assurance retraite » et une qui
    ne nomme que « Agirc-Arrco ». Seule la première compte. Une ligne de
    complémentaire seule ne compte que l'année où rien ne nomme la base
    seule : elle écrit alors une période que la base compte aussi, et sans
    elle la base validerait un trimestre que ses propres lignes n'atteignent
    pas.
  - **Son revenu est entier**, plafond franchi compris (plus haut).
  - **L'Ircantec y dit le contractuel public**, que le régime général couvre
    avec elle : une période « L'Assurance retraite, Ircantec » n'est pas un
    emploi du privé.

  Il ne porte pas la date de naissance en clair, mais son numéro de sécurité
  sociale en donne l'année et le mois, que la lecture reprend — le siècle se
  déduit de la première année travaillée. Le jour, que le numéro tait, le
  site le présume comme le modèle le fait quand on ne le dit pas, et le dit à
  l'assuré pour qu'il le corrige.

- **La coordination interrégimes.** Chaque régime liquide sur ses seules
  années, et la durée acquise dans chacun est comptée séparément — c'est le
  droit, et un régime et celui qui lui succède comptent pour un seul (voir
  §3). La **liquidation unique** (LURA), qui, depuis 2017, fait calculer par
  une seule caisse la retraite d'un polypensionné des trois régimes alignés,
  est servie depuis le 22 septembre 2026, avec la **proratisation croisée** de
  son salaire annuel moyen. En reste dehors sa troisième condition — la
  retraite de même nature déjà obtenue avant le 1er juillet 2017 —, qu'une
  carrière du dépôt, dont les régimes alignés liquident à la même date, ne
  peut pas porter.
