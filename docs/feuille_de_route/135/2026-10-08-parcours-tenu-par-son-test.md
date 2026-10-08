# Le parcours tenu par son test, que la conservation ne gèle plus

**Le 8 octobre 2026, à la demande du propriétaire** : le parcours de
présentation était pris entre deux tests. `tests/test_parcours.py` l'oblige à
suivre l'accueil et les pages ; la conservation le gelait, `zones.yaml` le
déclarant `recit`. Chaque chiffre qui bougeait sur une page rougissait donc la
suite, et la réparer demandait `conservation.py --figer --accepter-les-pertes`,
que le propriétaire devait autoriser à chaque fois : à l'étape 8 de
l'action 138, puis le 8 octobre au matin (`046e98a`).

- *Le diagnostic.* Le régime `recit` ne servait au parcours qu'à une chose :
  que `verifier_prose.py`, dont les sondes ne savent pas rendre une page, n'y
  demande pas d'ancres. Il lui valait aussi le gel, qui est le sens même du
  régime, et que rien ne justifiait : le parcours ne raconte pas, il dit ce
  que l'écran montre.
- *Un quatrième régime, `tenu`.* `zones.yaml` déclare
  `docs/parcours_presentation.md` `tenu`, avec `test: tests/test_parcours.py` :
  le document dit ce qui est vrai aujourd'hui, et le test qu'il nomme le
  confronte aux pages. C'est l'ancre `tenu(nom_du_test)` à l'échelle d'un
  document. `verifier_prose.py` ne l'ancre pas, et la conservation, qui ne
  gèle que `recit`, ne le gèle plus.
- *Rien de relâché pour les récits.* La règle tient en un endroit,
  `Zonage.faute_de_tenu` : le test nommé est un `tests/test_*.py` qui existe
  et nomme le document. Sans lui, `conservation.py` gèle le document comme un
  récit, et `verifier_prose.controler_tenus` le dit
  (`test_ce_qui_est_tenu_l_est_par_un_test_qui_le_lit`) ; un `test` nommé là
  où rien n'est `tenu` est refusé aussi. Les `paragraphes_recit` d'un document
  `tenu` restent gelés, et les dossiers gelés en entier (archives, décisions,
  versions) le restent quoi que `zones.yaml` en dise :
  `test_un_document_tenu_par_son_test_n_est_pas_gele` le joue sur un dépôt
  miniature, et rougit si la garde saute (essayé en la retirant).
- *La référence.* Refigée sans `--accepter-les-pertes` : elle quitte les
  66 paragraphes du parcours, et aucun autre, ni aucune entrée des
  registres ; elle prend la version de l'architecture et l'entrée du journal
  de veille du jour.
- *La prose.* `CLAUDE.md`, `docs/fraicheur.md`, les en-têtes de
  `verifier_prose.py` et de `zones.yaml` nomment le régime ; l'annexe B de
  l'architecture aussi, avec sa version
  (`2026-10-08-un-document-tenu-par-son-test.md`).

Désormais, une page qui bouge ne rougit plus que `test_parcours.py`, et le
parcours se répare en suivant la page, sans rien refiger.
