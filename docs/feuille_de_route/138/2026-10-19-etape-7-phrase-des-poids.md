# Étape 7, suite de la septième partie : la phrase des poids de la page Coût

**La demande.** Vague du 19 octobre 2026, session 24, la dernière de la
vague, lancée par la session de suivi sur la demande du propriétaire (« Lance
les sessions qui n'ont pas besoin de moi ») : ce que l'étape laisse aux pages,
le point 3 de « Ce qui reste » de la neuvième partie (note du 17 octobre, la
mortalité différentielle) et de la onzième (note du 19, les inaptes de la
Cnav). La table des poids de `pages.js` reste au propriétaire, comme les
départs qui suivent l'espérance de vie. Aucune règle du scénario 1 n'est en
cause : ni veille du droit, ni entrée au journal.

**La phrase.** Le dépliant « Les quatre systèmes comparés, du passé jusqu'à
2070 » (`coutDetailScenarios`) disait : « Les poids sont les effectifs réels
de chaque génération, lus dans la pyramide des âges de l'INSEE ; les écarts
viennent des treize cas types croisés avec 7 générations ». Depuis le 17
octobre, chaque cohorte de la grille survit au rythme de la population de son
diviseur, à nombre de décès égal (`cout._survies`, `cout._survies_alignees`) ;
depuis le 19, l'inapte, au rythme des inaptes de la Cnav, et la table des
poids le compte avec le salarié au SMIC (`cas_type_affiche`). La phrase dit
désormais : « Les poids sont les effectifs réels de chaque génération, lus
dans la pyramide des âges de l'INSEE. Dans chacune, chaque cas type survit,
depuis son départ, au rythme du vingtile de niveau de vie où son diviseur le
range, à nombre de décès égal : la pyramide garde ses survivants, et seule
change leur répartition entre fortes et faibles pensions. Le salarié reconnu
inapte au travail, compté avec le salarié au SMIC dans le dépliant « Ce que
chaque carrière type pèse dans ces chiffres », survit, lui, au rythme des
inaptes de la Cnav. » Les « treize cas types » qui suivent restent : la table
des poids n'en montre pas davantage, chaque variante de la grille y comptant
avec le cas type dont elle porte le code. Dans un dépliant, la phrase ne coûte
rien au budget de lecture de Coût.

**Le test** (`test_web.py`) :
`test_la_page_cout_dit_au_rythme_de_qui_chaque_cas_type_survit`, vu rouge
puis vert — la phrase, sous la référence, dont le diviseur suit le vingtile
(`POPULATION_PAR_NIVEAU_DE_VIE`) ; chaque variante de la grille du coût qui
vit à part (`CasType.mortalite`) nommée, avec le cas type dont la table la
compte et la population qu'elle suit ; la table rendue, qui a la ligne de ce
cas type et non une ligne de la variante. Une variante de plus qui vivrait à
part, l'ex-invalide de la Cnav, premier reste de l'étape, le fera tomber, et
se nommera.

**Ce que ça déplace.** La page Coût en ses quatre états (`cout`,
`cout_cascade_horizon`, `cout_cascade_hors_liste`, `cout_flux_horizon`), de
cette phrase seule ; aucun des 888 témoins de simulation ; ni le paquet.

**Trouvé en chemin.**

- *La table des poids* (`coutDetailPoids`) dit sous son tableau : « Une caisse
  réclamée par plusieurs cas types se partage également entre eux : la Cnav
  est celle des quatre carrières du privé ». Depuis le 19 octobre, l'inapte
  prend d'abord 8,37 % de la Cnav (`PART_INAPTES_CNAV`) et compte sur la
  ligne du salarié au SMIC, qui pèse 17,0 % des retraités de 2024 dans le
  paquet, le salarié au salaire moyen 12,4 % : le partage n'y est plus égal.
  C'est un texte de la table, que la session ne touche pas ; au propriétaire
  de le confier, avec la question des lignes de la CNRACL et de l'État (étape
  3). Une forme possible : « la Cnav est celle des quatre carrières du privé,
  à parts égales une fois servis ses inaptes, que la ligne du salarié au SMIC
  compte ».
- *Le paquet de `main` est périmé* : `test_le_paquet_est_a_jour` tombe, et,
  dans `-m rapide`, `test_les_annees_d_avant_1973_bornent_le_minimum_des_independants`
  (`test_simulateur.py`), qui le lit ; les deux tombent aussi sans cette
  retouche. Le commit du second (`b588364`, action 131) change les sources du
  paquet sans le refaire, ce que GitHub fait avant la suite complète.

**Ce qui reste**, de cette partie ; le reste de l'étape est dans son bloc.

1. *Au propriétaire* : la table des poids, ses lignes et sa phrase du partage
   (ci-dessus) ; le rapport de dépendance sous chaque variante (septième
   partie, point 3).
2. *À une session des pages, quand la grille changera* : la phrase, que le
   test lui montrera — l'ex-invalide de la Cnav, s'il entre dans la grille
   avec sa mortalité.
