# Étape 3 : la radiation des cadres à la limite d'âge, et ses exceptions

**Le 14 octobre 2026 : le fonctionnaire dont le départ saisi passe sa limite d'âge
est radié des cadres à la limite, reculée et prolongée par les exceptions qui
s'appliquent ; sa pension part de la radiation, et ses services s'y arrêtent. Le
militaire prend la limite la plus haute de sa catégorie. Python et JavaScript,
témoins compris (4d24d77, 71adf3c).**

## La décision

Le propriétaire a approuvé, ce 14 octobre, la proposition de la note de l'étape 2 :
la carrière de fonctionnaire s'arrête à la limite d'âge reculée et prolongée par les
exceptions qui s'appliquent, la pension de fonctionnaire part de ce jour, et ce qui
suit, jusqu'au départ saisi, peut être un métier de plus. De droit, les reculs pour
enfants ; présumées demandées et accordées autant que le départ saisi les demande, la
prolongation pour carrière incomplète, celle de l'actif et le maintien jusqu'à
70 ans ; le militaire à la limite la plus haute de sa catégorie ; les contractuels,
les ouvriers de l'État et les régimes spéciaux à une étape suivante.

## Ce que fait le modèle

- **`droit/limite_age.py`**, et son jumeau `moteur/js/droit/limite_age.js` :
  `radiation(moteur, carriere)` dit la radiation, sa date, la limite de l'emploi et
  chaque exception qui la recule, de quel âge à quel âge, de droit ou présumée ;
  `radier(moteur, carriere)` rend la carrière dont les services de fonctionnaire ou
  de militaire s'arrêtent à la radiation, l'année de la radiation gardée, que la date
  d'effet borne.
- **La limite se lit au jour où elle est atteinte** (date `age_atteint`), version par
  version : les sept fiches portent désormais leurs paramètres — les limites de
  chaque classe d'emploi (sédentaire, active, police et surveillance pénitentiaire,
  non-officier, officier), les paliers de 1977, 1978, 1985 et 1986, et le relèvement
  de la loi de 2010, compté depuis l'année où l'ancien âge d'ouverture est atteint
  (cinq ans sous la limite des civils, la limite même des militaires). Elles entrent
  au paquet par `FichesDatees`.
- **L'ordre de la loi** (relation `plafond_limite_age_fonction_publique`) : le recul
  pour enfants, un an par enfant de moins de vingt ans à la limite, trois au plus, ou
  un an pour le parent de trois enfants nés avant ses cinquante ans, le plus favorable
  des deux ; la prolongation pour carrière incomplète, depuis 2004, jusqu'à la durée
  du taux maximum, dix trimestres au plus ; puis celle de l'actif jusqu'à la limite
  des sédentaires, depuis 2010, ou le maintien du sédentaire jusqu'à 70 ans, depuis
  le 14 juin 2023 ; enfin le plafond de 70 ans.
- **Les départs** (`droit/departs.py`) : l'unité du code des pensions part à la
  radiation, motif `limite_d_age`, ou à l'ouverture si elle vient après ; le métier
  qui suit part au départ saisi. Le scénario 1 et l'échéancier liquident la carrière
  radiée. La présomption `exceptions_a_la_limite_d_age` est au vocabulaire et au
  § 5.6 de l'architecture.
- **Mesuré** : le sédentaire de l'État né en 1990, entré à 22 ans, touche la pension
  d'un départ à 70 ans, 5 219 € brut par mois en euros constants, qu'il saisisse 75,
  90 ou 119 ans ; le policier de la même génération, celle d'un départ à 67 ans,
  4 499 €. Trente-trois témoins existants baissent au scénario 1, de 2 à 24 % : les
  actifs nés de 1925 à 1945 et les militaires, dont le départ à 64 ans passait la
  limite. Six témoins neufs (`limite_age_*`) ; les 822 se retrouvent en JavaScript.

## Les choix, que le propriétaire peut reprendre

1. **Le corps n'est pas saisi.** Le sédentaire d'avant 1985 prend la limite du corps
   le plus haut, 70 ans puis 68, comme le militaire ; le policier celle du corps
   d'encadrement et d'application, 57 ans ; l'actif hors de la police 62 ans, 60
   avant la loi de 2010.
2. **L'actif avant 2010 n'est pas prolongé** : l'article 2 du décret n° 48-1907, que
   le décret n° 53-711 lui laisse, n'est pas lu, et la fiche dit « aucun maintien de
   droit commun ». D'où les baisses des actifs nés avant 1950.
3. **La prolongation pour carrière incomplète compte les services seuls**, sans les
   bonifications que L. 13 y ajoute : elle peut accorder un peu trop.
4. **Les comptes notionnels gardent la carrière saisie** : la radiation ne vaut
   qu'au scénario 1. Faut-il que la proposition arrête, elle aussi, les services à
   la limite ? C'est le droit du statut, pas celui de la retraite.

## Deux constats, hors de l'étape

- **Une pension servie avant le départ n'est pas revalorisée au-delà des données** :
  `mener_au_mois` la mène d'un coefficient 1 dans la projection, si bien que le
  sédentaire né en 1990 radié à 70 ans et saisi parti à 75 voit sa pension, aux euros
  de 2026, à 4 785 € au lieu de 5 219 €. La pension militaire servie à la sortie de
  l'armée l'était déjà. À vérifier par la session du modèle.
- **Depuis 2015, l'activité qui suit une première pension n'ouvre plus de droits**
  (L. 161-22-1 A) : le métier exercé après la radiation, liquidé au départ saisi,
  garde au modèle ses droits, comme tout départ multiple (`droit/departs.py`).

## Ce que la page doit dire (session du site)

Le motif `limite_d_age` a reçu, pour que la page ne dise pas « undefined », une ligne
dans `POURQUOI_CE_DEPART` et `POURQUOI_PAS_A_CETTE_DATE` (`moteur/js/pages.js`), et
le module son préchargement (`index.html`). Le reste est au site : le bandeau d'un
départ unique (`departs[0].motif === "limite_d_age"`), qui dit « la loi vous radie
des cadres à 70 ans » ; l'exception présumée, nommée — « nous présumons que vous avez
demandé et obtenu le maintien jusqu'à 70 ans », de même la prolongation pour carrière
incomplète et celle de l'actif —, et le recul de droit pour enfants ; la limite du
militaire, la plus haute de sa catégorie ; et, quand le départ saisi la passe, que
les années suivantes ne sont plus du service et peuvent être un métier de plus. Tout
se lit dans `radiation(moteur, carriere)` : `date`, `age`, `limite`, `classe`,
`reculs` et `presumees`.

## Ce qui reste

- La limite des agents contractuels, des ouvriers de l'État et des régimes spéciaux,
  une fiche chacun.
- Les lectures que les fiches gardent : les lois de 1946 et 1947, le décret
  n° 48-1907, la limite des territoriaux avant 1985, les limites des corps actifs
  avant 2010, les tableaux de L. 4139-16 de 2007 à 2023.
- La CARMF complémentaire avant 2017 et le taux acquis au 31 mars 1983, que l'étape
  1 signalait.
