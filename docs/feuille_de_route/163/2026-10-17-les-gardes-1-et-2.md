# Les gardes 1 et 2

**Le 17 octobre 2026, la demande.** Le propriétaire, le classement des rouges
lu : « Fais les gardes 1 et 2 ».

**La garde 2, le bloc « Reprise » à l'envoi.** Quand un commit à publier
touche la feuille de route ou ses notes, `scripts/pousser.sh` joue leurs deux
tests de `tests/test_prose.py` — le bloc « Reprise » de chaque action en
cours, le rangement des notes —, en 0,7 s sur le dépôt, et refuse s'ils
rougissent. Un envoi qui n'y touche pas ne les joue pas. Les tests, dans
`tests/test_pousser.py`, sur un atelier dont la feuille de route manque son
bloc, puis le reçoit ; un autre tient les deux noms que le script cite.

**La garde 1, les chiffres cités produits plutôt que gardés.**

- *Les comptes du parcours* (neuf rouges) : les huit que les pages Données et
  Avantages tirent du paquet sont ancrés sur `moteur/donnees.json`, que GitHub
  refait avant de récrire les ancres. Deux outils de plus pour les sondes : la
  sonde `somme` (les valeurs recontrôlées, série par série) et les filtres
  croisés d'`entrees`, par `&` et `!=` (les dispositifs en vigueur, hors écarts
  structurels et sans date de fin). Le neuvième, « les 48 points » qui
  séparent deux carrières, est un rapport que la grille des cas types calcule
  et qu'aucune sonde ne refait : le parcours dit désormais « l'écart qui les
  sépare », que la page affiche. `tests/test_parcours.py` lit le parcours sans
  ses ancres, et refuse tout compte écrit à la main.
- *Le README* (un rouge) : ses deux comptes de statuts et de régimes étaient
  dans des blocs de code, où une ancre ne vit pas ; ils en sortent, le compte
  des fiches de régime restant ancré plus haut. Le test qui les recomptait
  refuse désormais tout compte écrit à la main.
- *L'accueil* (trois rouges) : `MESURES_BLOCAGES`, les douze mesures que ses
  points de blocage citent, est récrit par `scripts/mesures_accueil.py`, qui
  les refait comme leurs tests — le coût par défaut, `solde_fusion.py` sous
  l'hypothèse A, la variante prospective, la TVA, le diviseur de l'âge de
  l'assuré —, en une minute. `regenerer.py` le lance entre le paquet et les
  témoins, qui rendent l'accueil. Sur le modèle du jour, il retrouve les
  douze valeurs écrites. Les tests qui les tiennent restent.

**Ce qui reste écrit à la main.** Les chiffres à unité du parcours — les
tableaux de ses carrières, les montants des pages Programme et Avantages, près
de quatre-vingt-dix en tout —, dont trois rouges venaient (les carrières
rejouées deux fois, le Programme une) ; et « les 23 que le modèle chiffre »,
que la cascade de la page Avantages compte et qu'aucun test ne lit. Les
produire demande des mesures du modèle par carrière : une étape à elle.
