# Les revenus au-delà de l'âge de départ choisi : 1 % de plus par an, puis l'action close

**Le 12 octobre 2026, le propriétaire toujours connecté à « Mon estimation
retraite » : la question que la note du même jour laissait ouverte est
tranchée, et l'action se clôt.**

- *La demande.* « Action 142 » : ce qui restait, la question ouverte et la
  clôture. La note du prix d'achat avait vu, sous des revenus plats, chaque
  année travaillée après l'âge légal gagner encore 1 % de points, sans en
  savoir la cause.
- *La méthode, sans aucune donnée du propriétaire.* La même situation
  fictive, salarié du privé à 30 000 € bruts par an, rien n'étant enregistré ;
  la série de « Lire les données de l'évolution des revenus » ; les points
  Agirc-Arrco « retenus pour le calcul » de départs successifs, dont la
  différence isole les mois qui les séparent, sous des revenus plats, puis
  sous une croissance régulière jusqu'à 36 000 €, un départ plus tardif
  ajouté. Ni les totaux, ni les âges, ni les années de la carrière d'essai
  ne sont recopiés.
- *Ce que la page fait.* La série de revenus qu'elle laisse saisir s'arrête à
  l'année de l'« âge de départ choisi » : le premier des âges proposés, puis,
  les lignes de départ dépliées, la dernière dépliée. Pour un départ plus tardif, elle prolonge le revenu de cette
  année-là de 1 % par an, composé, à compter du 1er janvier suivant, quelle
  que soit l'évolution choisie : sous des revenus plats comme sous une
  croissance régulière, cette règle et le prix d'achat figé après 2037
  redonnent les points au centième. Les « 1 % de points » de plus par année
  ajoutée sont ce revenu prolongé, non le prix.
- *En chemin.* La projection par défaut, avant toute saisie, fait déjà
  croître le revenu de 1 % par an, composé ; c'est la croissance régulière
  saisie qui est linéaire jusqu'au revenu de fin de carrière. Choisie après
  des revenus plats, elle propose pour ce revenu la projection de la page à
  l'âge choisi, prolongement compris. Pour la carrière du propriétaire,
  confrontée sous la projection par défaut, la convention du modèle
  (`--revenus-futurs prix --croissance 1.0`) reste donc celle de la page,
  avant comme après l'âge légal.
- *Ce qui change.* La fiche `agirc_arrco_valeur_achat` dit la règle, à la
  place du « non vérifié ». Le modèle ne change pas.
- *La clôture.* Rien n'attend plus le propriétaire. L'action passe, telle
  quelle, à la fin de `docs/archives/feuille_de_route.md`, ses notes sous
  `docs/archives/feuille_de_route/142/` ; Ines, le dernier modèle à exécuter
  à part, reste à l'action 137, qui le porte déjà.
