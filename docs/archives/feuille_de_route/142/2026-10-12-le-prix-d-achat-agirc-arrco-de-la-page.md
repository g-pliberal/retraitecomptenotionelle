# Le prix d'achat Agirc-Arrco de « Mon estimation retraite » : 1 % de plus par an jusqu'en 2037, puis figé

**Le 12 octobre 2026, peu après minuit : le propriétaire connecté à « Mon
estimation retraite », le dernier point de l'action est mesuré.**

- *La demande.* « Fais le point 1, Mon estimation retraite » : le prix d'achat
  Agirc-Arrco implicite de la page, que la note du 4 octobre avait laissé à
  expliquer — « rapporté au revenu, 11,6 % de plus que celui de 2026 », avec
  des points qui semblaient les mêmes chaque année sous des revenus plats.
- *La méthode, sans aucune donnée du propriétaire.* Dans le navigateur de
  l'application, le propriétaire connecté lui-même par FranceConnect, rien
  n'étant enregistré : une situation actuelle fictive — salarié du privé, temps
  plein, 30 000 € bruts par an, sous le plafond, donc en tranche 1 seule au
  taux de calcul de 6,20 % —, des revenus futurs « Pas d'évolution », vérifiés
  plats dans « Lire les données de l'évolution des revenus », puis les points
  « retenus pour le calcul » de l'Agirc-Arrco à plusieurs âges de départ, et
  sous un temps partiel à 50 % commencé au 1er janvier 2027, puis au 1er janvier
  2028. Une différence de points isole les années qui séparent deux
  simulations ; rapportée à ce qu'achèterait le prix de 2026, 20,1877 €, elle
  donne le prix que la page prête à ces années. Les points du propriétaire
  lui-même n'entrent dans aucun calcul.
- *Ce que la page fait.* Les points de 2027 valent 99,0 % de ceux du prix de
  2026 : un prix supérieur de 1 %. Ceux de l'année de l'âge légal de la
  carrière d'essai, bien après 2037, en valent 89,63 %, soit 1/1,01¹¹. Et la règle « 1 % de plus par an jusqu'en 2037, puis plus rien »
  redonne la somme des années de 2028 à l'âge légal à 0,01 % près. 2037 est
  l'horizon jusqu'où l'annexe de l'accord du 5 octobre 2023 projette les valeurs
  du régime ; au-delà, la page fige le prix, quand l'accord le fait suivre au
  salaire moyen, comme le modèle. Les « 11,6 % » du 4 octobre étaient ce prix
  figé, 1,01¹¹ ; et la complémentaire du modèle reste sous celle de la page
  d'autant plus qu'on travaille longtemps après 2037.
- *En chemin.* La croissance « régulière » des revenus est linéaire, du revenu
  actuel au revenu de fin de carrière, que la page propose à 1 % par an composé ;
  les revenus futurs pèsent bien sur les points de la complémentaire, qui ne
  les ignore pas. Après l'âge légal de la carrière d'essai, chaque année
  ajoutée gagne encore environ 1 % de points : la page y prolonge peut-être le
  revenu au-delà de la fin de carrière saisie, ce qui n'est pas vérifié.
- *Ce qui change.* La fiche `agirc_arrco_valeur_achat` porte la mesure, en
  lecture divergente. Le modèle ne change pas : il suit l'accord, et le
  simulateur individuel dit déjà, dans sa bulle, que la convention de la page
  est autre. L'action n'a plus rien qui demande le propriétaire : elle se clôt.

**La même nuit : la carrière du propriétaire, reconfrontée au modèle d'aujourd'hui.**

- *Les pièces.* L'estimation rapide recopiée le 4 octobre, hors du dépôt, et le
  relevé de carrière tous régimes, retéléchargé par le propriétaire connecté et
  rangé dans le répertoire de la session ; `scripts/estimation_officielle.py`,
  qui n'imprime rien d'autre que des écarts au dépôt. Trois choses apprises en
  chemin : le texte d'un relevé gardé par une session du 4 octobre n'en était
  qu'un extrait, qui perdait onze trimestres ; les deux corrections manuelles
  de l'estimation visaient le relevé du seul régime général, et le relevé tous
  régimes n'en demande aucune ; et le script prolonge, pour les années à venir,
  le statut de la ligne principale de la dernière année du relevé, quand la page
  prolonge la situation actuelle — l'extrait, qui finissait sur un contrat
  public, envoyait ainsi toute la complémentaire à l'Ircantec, ce que le relevé
  entier ne fait pas.
- *Ce qui concorde.* Les trimestres, aux trois âges de la page ; la retraite de
  base, à moins d'un millième près, quand la carrière à venir suit la
  convention de la page, les prix plus 1 % par an — comme le 4 octobre, après
  plus de deux cents commits.
- *Ce qui ne concorde pas.* La complémentaire du modèle ressort de 3,2 à 4,1 %
  sous celle de la page, et le total de 0,8 à 0,9 % : le sens et l'ordre de ce
  que donne la valeur d'achat que la page fige après 2037, pour une carrière
  qui continue longtemps au-delà. Sous la convention du modèle, le salaire
  moyen, la base ressort de 6,2 à 7,1 % plus bas, la complémentaire de 7,3 à
  8,6 %, le total de 6,5 à 7,5 % : une hypothèse de projection, non une règle.
