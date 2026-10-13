# La dernière année incomplète d'un relevé, dite à qui le dépose

**Le 14 octobre 2026 : un deuxième relevé réel, confronté au site en session
locale, s'arrête avant la fin de sa dernière année ; le site le dit
désormais à qui dépose son relevé, et l'invite à compléter.**

- *La confrontation.* Le relevé est passé par le chemin du site — le PDF en
  lignes, puis en saisie, en Python et en JavaScript —, puis par le relevé
  des droits du scénario 1 (`droit/releve.construire`) et par la page
  `/simuler` que node rend, au moyen de scripts privés gardés hors du dépôt.
  La lecture est la même des deux côtés ; les trimestres, la durée requise et
  les points Agirc-Arrco des années pleines sont ceux du relevé, au centième.
  Les écarts de la seule dernière année sont décrits à l'action.
- *Où.* Comme la réserve du relevé incomplet avant le départ (action 137) :
  dans une note de la lecture, qui naît dans `releve_lu.py` et que son jumeau
  `releve-lu.js` porte mot pour mot ; `index.html` l'affiche sous le champ de
  dépôt.
- *La règle.* La lecture retient la date où finit la période datée la plus
  tardive : la seconde date d'une ligne qui en porte deux, avec ou sans
  revenu, une maladie couvrant ses mois autant qu'un emploi. Quand cette date
  tombe dans la dernière année lue, avant décembre, la note paraît. Il faut
  qu'un mois entier manque, puisque le modèle compte en mois : une période
  finie le 19 décembre, comme dans le relevé d'essai de 2026, n'appelle
  aucune note. Un relevé qui ne date pas ses périodes n'en reçoit aucune non
  plus.
- *La phrase*, sur le relevé d'essai : « Le relevé s'arrête le 14 juin 2019 :
  les droits les plus récents n'y sont peut-être pas encore enregistrés. La
  simulation compte pourtant chaque ligne pour une année entière, sauf celle
  du départ, et prolonge jusqu'à lui le revenu de la dernière. Si vous avez
  travaillé depuis, ajoutez au revenu de 2019 ce que vous avez gagné après
  cette date, puis une ligne par année ; sinon, déclarez les années sans
  emploi dans « Interruptions ». » La première phrase redit ce que le relevé
  d'info-retraite annonce lui-même ; la deuxième, la convention de la page de
  résultats. Le premier du mois s'écrit « 1er ».
- *Ce qui change.* Un relevé d'essai inventé, dont la dernière année s'arrête
  en juin, entre aux relevés que les deux moteurs lisent ensemble, ainsi que
  sa variante finie un premier du mois. Deux tests s'y ajoutent : la note et
  sa date, à quatre fins d'année possibles ; et la période la plus tardive,
  maladie comprise, sans note pour les relevés sans dates ou finis en
  décembre. Changent aussi la phrase de la page de résultats
  (`resumeReleve`), qui disait que le relevé ne donne jamais le mois, avec sa
  ligne du témoin des pages, la docstring du lecteur et
  `docs/limites/5-hors-du-modele.md`. Aucun montant ne bouge.
- *Ce qui reste.* Les correctifs b et c, non décidés. Et le début d'une
  dernière année : un emploi commencé à l'automne, sans rien avant, est
  prolongé lui aussi comme une année entière. La note n'en dit rien, puisqu'elle
  ne regarde que la fin.
