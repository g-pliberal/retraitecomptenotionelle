# La carte des fiches : les quatre fiches presque mûres, mûries

Session 2 de la première salve de la vague du 19 octobre 2026, sans le
propriétaire. Son point, une étape de « Faire mûrir la carte » : les quatre
fiches que la note du 18 octobre laissait presque mûres
(`130/2026-10-18-carte-des-fiches-limite-d-age.md`, « Ce que l'étape
laisse »), à qui ne manquaient que six champs. Aucun chiffre du modèle ne
bouge, ni le paquet du site, ni les témoins : `regenerer.py --verifier` ne
trouve périmé que le tableau de bord, que GitHub refait.

## Ce qui est fait

- **Le test d'abord**, `test_les_fiches_presque_mures_le_sont`
  (`tests/test_carte.py`) : les quatre fiches ne manquent de rien, et ce
  qu'elles disent d'elles-mêmes tient. Vu rouge sur leurs six manques. Le
  contrôle que le test de la limite d'âge faisait de ses quinze fiches est
  passé dans `tests/outils_carte.py`, que les deux tests appellent : les
  approximations touchent des versions de la fiche ; le code nomme des
  fonctions que chaque moteur définit, des tests qui existent, en liste ou
  dans une phrase, et ses paramètres sous l'une de trois formes — tous ceux
  des versions et rien d'autre, des champs des périodes des fiches de régime
  qu'elle concerne quand ses versions n'en portent pas, ou « aucun », et la
  raison.
- **`rafp_majoration_capital` dit son étape**, la liquidation de chaque
  régime. Elle attendait qu'une couche sache excepter une fiche de son
  sélecteur : la couche des comptes notionnels neutralise cette étape et garde
  le RAFP par son nom, deux décisions que la pile refusait. Une opération de
  couche porte désormais `sauf`, champ additif du contrat C.4 : les fiches que
  son sélecteur n'atteint pas, que la couche décide par leur nom
  (`noyau/univers.py`, `Operation.visees`). L'exception ne vaut que pour un
  sélecteur qui se résout en fiches, hors d'une couche d'un seul calcul, dont
  le moteur neutralise le domaine entier, et nomme une fiche de la carte que
  le sélecteur atteint ; le test
  `test_une_couche_excepte_de_son_selecteur_ce_qu_elle_decide_par_son_nom` l'a
  vu rouge. Les univers ne changent pas : le paquet les porte résolus, sans
  leurs décisions, et chacun garde 130 fiches du droit réel sans décision sur
  245. Le code du RAFP nomme ses paramètres.
- **`asv_autres_professions_de_sante`** a son code — l'acquisition des
  points, la part de l'assurance maladie, la liquidation, le compte et la
  fiche de paie, dans les deux moteurs ; les champs des quatre fiches de
  régime — et neuf approximations, transcrites de ce que ces fiches
  déclaraient manquer et de ce que la fiche laissait à relire, chacune
  rattachée aux versions qu'elle touche : les points d'avant les forfaits en
  euros, présumés ; les valeurs de service des points d'avant 2006 ; le
  partage avec l'assurance maladie et les âges, lus pour 2025 ; l'arrondi et
  l'année du revenu de l'ajustement ; les montants projetés sur les prix ; la
  borne de 420 points du chirurgien-dentiste ; le rachat ; les règlements de
  2026, non lus. Toutes « non mesuré », comme les fiches le disaient.
- **`cultes_retraite_complementaire_taux_specifiques`** a trois versions de
  la période de cotisation, coupées aux circulaires lues : avant 2020, le taux
  de base seul, supposé, aucune circulaire n'étant lue ; de 2020 à
  septembre 2021, un seul taux publié, que la circulaire suivante dit
  « inchangé » ; depuis octobre 2021, les huit taux spécifiques. Trois de ses
  textes à rattacher y sont entrés tels quels ; le quatrième, les conventions
  de la CAVIMAC avec l'Arrco, non publiées, avec sa question, va aux textes à
  relire. Son code dit où le modèle achète les points au taux de base, et
  prélève la contribution d'équilibre sur le forfait. Elle reste à vérifier.
- **`minimum_pension_ieg`**, d'une règle manquante, a le code des fonctions
  où elle manque — la liquidation, le complément, la réversion, dans les deux
  moteurs —, aucun paramètre, et les tests des pensions des IEG. Elle reste
  manquante.

La carte passe de 111 fiches à mûrir à 107, et de 806 manques à 800 : les 107
sont celles que la phase 2 a tirées du registre de veille, à lire au droit.
`conservation.py --depuis HEAD` dit changée la ligne de veille des cultes,
refaite depuis la fiche : ses textes à rattacher sont passés dans ses
versions, ce que la référence figée admet.

L'index LEGI n'a pas été remis à jour : l'étape n'écrit aucune règle du
scénario 1, et le journal de veille n'a pas d'entrée.

## Ce que l'étape laisse

- Le test du code étendu à toutes les fiches, après la vague : sur la tête de
  `main`, 165 fiches ont un code, et seules les dix-neuf que l'action a fait
  mûrir l'écrivent sous la forme que `outils_carte.py` lit. Les 146 autres
  l'écrivent en prose : leurs paramètres (139), leurs fonctions Python (128) et
  JavaScript (117), leurs tests (50). Étendre le test, c'est d'abord récrire
  ces champs.
- `code` n'est toujours pas parmi les champs documentaires de `memoire.py`.
- Les 107 fiches à lire au droit, et les points ouverts des phases 2 à 8 que
  la note du 18 octobre relève.
- Le minimum des IEG attend la convention sur les ressources de l'année qui
  précède le versement, à décider avant de l'écrire ; la session 138.9 pose la
  même question pour le minimum de pension de la SNCF.

## Ce qui attend le propriétaire

Ce que les fiches disent déjà, d'ici illisible : ce qu'achète chaque taux
spécifique des cultes, à demander à la CAVIMAC ou à Malakoff Humanis
Agirc-Arrco, et la page des montants de 2019 de la CAVIMAC, que l'archive du
web garde peut-être et que le réseau de la session refuse. Pour le reste, rien
de neuf : la décision de la proposition du sixième domaine, et celle sur la
retraite progressive, le cumul et la seconde pension, README muet.
