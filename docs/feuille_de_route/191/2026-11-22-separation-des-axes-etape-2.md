# Les fichiers de régime en quatre blocs : la liquidation séparée de la cotisation

**Reprise, au 22 novembre 2026.** Les 80 fichiers de régime calculés
s'écrivent en quatre blocs : la structure, la liquidation au jour de la
date d'effet, la cotisation à l'année, le montant servi. Le moteur lit encore
des périodes, que le chargeur Python refait de ces blocs, à l'identique
(`donnees/axes.py`, `vue_ancienne`). Les données sont gelées : aucun champ de
période ne s'ajoute, aucune période ne se coupe, et aucun résultat ne bouge
jusqu'au retrait de cette vue. Reste, dans l'ordre de l'amendement du
22 novembre à la note 0009 : le moteur qui lit les blocs, puis le Python, le
paquet et les tests, puis le retrait de la vue. Par quoi commencer : le
moteur. L'oracle, hors du dépôt, est sous
`architecture/separation-des-axes/oracle/` dans les fichiers du projet.

**La demande.** Le 22 novembre 2026, le propriétaire choisit de séparer
complètement les deux axes des fichiers de régime (« on prend complète
alors »), puis valide la classification des 144 champs : 92 de la
liquidation, 39 de la cotisation, 6 du montant servi, 7 de la structure.
Cette session mène la deuxième étape, et elle seule : la nouvelle forme
devient la source, l'ancienne une vue fabriquée, le moteur intact. Sur
Opus 5.5 ; Fable 5.2 étant indisponible jusqu'au 25 novembre, la relecture
s'est faite sur Opus, dans un contexte neuf.

**Ce qui est fait.** L'amendement est ajouté à la note 0009, avec le relevé
de la classification (`docs/decisions/0009/separation-des-axes/`). Un script
hors du dépôt a migré les 80 fichiers en recopiant le texte de chaque champ,
commentaires compris : 13 268 lignes retirées, 5 944 écrites ; 322 lignes de
liquidation, 58 de servi, 875 de cotisation. Pour chaque fichier, il a exigé
que la vue refasse la fiche d'hier à l'égalité près, et qu'aucun commentaire
ne se perde. Les lecteurs qui lisaient le YAML en direct passent par le
chargeur (`lire_fiche_de_regime`, `fiche_de_regime`).

**Relu sur Opus, dans un contexte neuf.** La relecture a refait les fiches
d'hier depuis le dernier commit et les a trouvées égales à la vue dans les
114 fichiers, et les 450 commentaires du YAML tous là. Elle a trouvé des cas
que les données n'ont pas et que la vue aurait mal refaits sans un mot : un
trou ou un début tardif de la liquidation ou du servi, un servi qui se
chevauche, une cotisation hors du 1er janvier, une tranche qui se chevauche,
un fichier qui porterait encore ses périodes. La vue les refuse désormais,
chacun avec son test.

**Vérifié.** L'oracle, refait sur `main` à 033e864 avant toute migration,
est identique après. Le paquet du site (`moteur/donnees.json`) se refait au
caractère près : les témoins, que le portage calcule depuis lui seul, ne
peuvent bouger.

**Ce qui reste à reprendre quand la vue partira.** La cotisation garde une
ligne par période d'hier, même là où rien n'y change, parce que la vue en a
besoin pour refaire les bornes des périodes ; elle se resserre quand la vue
part. Une date d'effet au jour (56 périodes en déclaraient une) se rend à la
frontière d'années la plus proche dont le 1er janvier n'est pas déjà une
borne : la règle refait les 80 régimes, mais n'est qu'une règle de la vue,
qui part avec elle. La note d'une période d'hier est allée, par position, à
la ligne de liquidation qui s'ouvre le même jour, sinon à sa ligne de
cotisation : la relecture en a compté au moins 80, sur les 322 lignes de
liquidation, qui parlent de cotisation (le taux appelé de l'Agirc, la
première tranche de la CNAVPL). Elles se rangent à la main quand la vue part ;
d'ici là, la vue préférant la note de la cotisation, une note déplacée de la
liquidation vers la ligne de cotisation de sa période ne change rien. Le
poids des annuités de la caisse des membres du CESE,
que l'amendement range dans la cotisation, reste pour l'heure dans la
liquidation, comme la durée requise qui le porte : c'est l'étape du moteur
qui le déplacera.
